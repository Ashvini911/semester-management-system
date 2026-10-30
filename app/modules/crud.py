from dataclasses import dataclass
from datetime import date, time
import re

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for
import mysql.connector

from app.database.connection import query
from app.services.permission_service import actions_for
from app.utils.decorators import permission_required


@dataclass(frozen=True)
class FormField:
    name: str
    label: str
    kind: str = "text"
    required: bool = True
    max_length: int | None = None
    minimum: int | None = None
    maximum: int | None = None
    choices: tuple[str, ...] = ()
    lookup_sql: str | None = None
    lookup_value: str | None = None
    lookup_label: str | None = None
    readonly: bool = False


@dataclass(frozen=True)
class ModuleSpec:
    slug: str
    title: str
    table: str
    key: str
    fields: tuple[FormField, ...]
    list_sql: str
    columns: tuple[tuple[str, str], ...]
    search_columns: tuple[str, ...] = ()


def _lookup_options(field):
    if field.lookup_sql:
        return query(field.lookup_sql)
    if field.choices:
        return [{"value": value, "label": value} for value in field.choices]
    return []


def _form_value(field, raw):
    value = raw.strip()
    if not value:
        if field.required:
            raise ValueError(f"{field.label} is required.")
        return None
    if field.max_length and len(value) > field.max_length:
        raise ValueError(f"{field.label} must be {field.max_length} characters or fewer.")
    if field.kind == "number":
        try:
            numeric_value = int(value)
        except ValueError as error:
            raise ValueError(f"{field.label} must be a whole number.") from error
        if field.minimum is not None and numeric_value < field.minimum:
            raise ValueError(f"{field.label} must be at least {field.minimum}.")
        if field.maximum is not None and numeric_value > field.maximum:
            raise ValueError(f"{field.label} must be no more than {field.maximum}.")
        return numeric_value
    if field.kind == "date":
        try:
            date.fromisoformat(value)
        except ValueError as error:
            raise ValueError(f"{field.label} must be a valid date.") from error
    elif field.kind == "time":
        try:
            time.fromisoformat(value)
        except ValueError as error:
            raise ValueError(f"{field.label} must be a valid time.") from error
    elif field.kind == "email" and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
        raise ValueError(f"{field.label} must be a valid email address.")
    return value


def _validate(fields):
    values = {}
    errors = []
    for field in fields:
        try:
            value = _form_value(field, request.form.get(field.name, ""))
            options = _lookup_options(field)
            if value is not None and field.lookup_sql:
                allowed = {str(option[field.lookup_value]) for option in options}
                if value not in allowed:
                    raise ValueError(f"Choose a valid {field.label.lower()}.")
            elif value is not None and field.choices and value not in field.choices:
                raise ValueError(f"Choose a valid {field.label.lower()}.")
            values[field.name] = value
        except ValueError as error:
            errors.append(str(error))
    if "Start_Date" in values and "End_Date" in values:
        if date.fromisoformat(values["End_Date"]) <= date.fromisoformat(values["Start_Date"]):
            errors.append("End date must be after start date.")
    return values, errors


def _database_feedback(error):
    if error.errno == 1062:
        return "A record with the same unique value already exists."
    if error.errno in {1451, 1452}:
        return "The selected related record is invalid or is still in use."
    return "The database could not save this record. Check the values and try again."


def create_crud_blueprint(spec):
    blueprint = Blueprint(spec.slug, __name__, url_prefix=f"/{spec.slug}")
    editable_fields = tuple(field for field in spec.fields if not field.readonly)

    def render_form(row, editing, errors=None):
        lookups = {
            field.name: _lookup_options(field)
            for field in spec.fields
            if field.lookup_sql or field.choices
        }
        return render_template(
            "modules/form.html",
            spec=spec,
            row=row,
            editing=editing,
            lookups=lookups,
            errors=errors or (),
        )

    @blueprint.get("/")
    @permission_required(spec.slug, "R")
    def index():
        search = request.args.get("q", "").strip()
        sql = spec.list_sql
        params = ()
        if search and spec.search_columns:
            where = " OR ".join(f"LOWER({column}) LIKE LOWER(%s)" for column in spec.search_columns)
            if " ORDER BY " in sql.upper():
                split_at = sql.upper().rindex(" ORDER BY ")
                source, ordering = sql[:split_at], sql[split_at:]
                sql = f"{source} WHERE {where}{ordering}"
            else:
                sql = f"{sql} WHERE {where}"
            params = tuple(f"%{search}%" for _ in spec.search_columns)
        rows = query(sql, params)
        return render_template(
            "modules/list.html",
            spec=spec,
            rows=rows,
            actions=actions_for(session.get("role"), spec.slug),
            search=search,
        )

    @blueprint.route("/new", methods=["GET", "POST"])
    @permission_required(spec.slug, "C")
    def new():
        if request.method == "POST":
            values, errors = _validate(spec.fields)
            if errors:
                return render_form(request.form, editing=False, errors=errors), 400
            names = tuple(values)
            placeholders = ", ".join(["%s"] * len(names))
            columns = ", ".join(f"`{name}`" for name in names)
            try:
                query(
                    f"INSERT INTO `{spec.table}` ({columns}) VALUES ({placeholders})",
                    tuple(values[name] for name in names),
                    write=True,
                )
            except mysql.connector.Error as error:
                current_app.logger.exception("Database insert failed for %s", spec.slug)
                flash(_database_feedback(error), "error")
                return render_form(request.form, editing=False), 400
            flash(f"{spec.title[:-1] if spec.title.endswith('s') else spec.title} created.", "success")
            return redirect(url_for(f"{spec.slug}.index"))
        return render_form({}, editing=False)

    @blueprint.route("/<path:key>/edit", methods=["GET", "POST"])
    @permission_required(spec.slug, "U")
    def edit(key):
        rows = query(
            f"SELECT * FROM `{spec.table}` WHERE `{spec.key}` = %s",
            (key,),
        )
        if not rows:
            abort(404)
        row = rows[0]
        if request.method == "POST":
            values, errors = _validate(editable_fields)
            if errors:
                return render_form(request.form, editing=True, errors=errors), 400
            assignments = ", ".join(f"`{name}` = %s" for name in values)
            try:
                query(
                    f"UPDATE `{spec.table}` SET {assignments} WHERE `{spec.key}` = %s",
                    tuple(values[name] for name in values) + (key,),
                    write=True,
                )
            except mysql.connector.Error as error:
                current_app.logger.exception("Database update failed for %s", spec.slug)
                flash(_database_feedback(error), "error")
                return render_form(request.form, editing=True), 400
            flash(f"{spec.title[:-1] if spec.title.endswith('s') else spec.title} updated.", "success")
            return redirect(url_for(f"{spec.slug}.index"))
        return render_form(row, editing=True)

    @blueprint.post("/<path:key>/delete")
    @permission_required(spec.slug, "D")
    def delete(key):
        try:
            deleted = query(
                f"DELETE FROM `{spec.table}` WHERE `{spec.key}` = %s",
                (key,),
                write=True,
            )
            if not deleted:
                abort(404)
        except mysql.connector.Error as error:
            current_app.logger.exception("Database delete failed for %s", spec.slug)
            flash(_database_feedback(error), "error")
        else:
            flash(f"{spec.title[:-1] if spec.title.endswith('s') else spec.title} deleted.", "success")
        return redirect(url_for(f"{spec.slug}.index"))

    return blueprint
