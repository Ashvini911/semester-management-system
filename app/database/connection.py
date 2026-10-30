from datetime import timedelta
import logging
import os

from flask import current_app, g, has_app_context, has_request_context, session
import mysql.connector


ROLE_NAMES = {
    "AR_OFFICER": "r_ar",
    "HOD": "r_hod",
    "DEAN": "r_dean",
    "CLERK": "r_clerk",
}


def _active_role():
    if has_request_context():
        return ROLE_NAMES.get(session.get("role"), "r_auth")
    return "r_auth"


def _configured_value(name):
    if has_app_context():
        return current_app.config[name]
    return {
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_USER": os.getenv("DB_USER", "semester_app"),
        "DB_PASS": os.getenv("DB_PASS", ""),
        "DB_NAME": os.getenv("DB_NAME", "semester_mgt"),
        "DB_PORT": int(os.getenv("DB_PORT", "3306")),
        "DB_CONNECT_TIMEOUT": int(os.getenv("DB_CONNECT_TIMEOUT", "5")),
    }[name]


def _log_database_failure(stage, host, database, role):
    log = (
        current_app.logger
        if has_app_context()
        else logging.getLogger(__name__)
    )
    log.exception(
        "MySQL connection setup failed during %s (host=%s, database=%s, role=%s)",
        stage,
        host,
        database,
        role,
    )


def get_connection(role=None):
    active_role = role or _active_role()
    if active_role not in {"r_auth", *ROLE_NAMES.values()}:
        raise ValueError("Unknown database role requested by the application.")
    if has_app_context():
        connection = g.get("database_connection")
        if connection is not None and g.get("database_role") == active_role:
            return connection
        if connection is not None:
            connection.close()
            g.pop("database_connection", None)
            g.pop("database_role", None)

    host = _configured_value("DB_HOST")
    database = _configured_value("DB_NAME")
    try:
        connection = mysql.connector.connect(
            host=host,
            user=_configured_value("DB_USER"),
            password=_configured_value("DB_PASS"),
            port=_configured_value("DB_PORT"),
            connection_timeout=_configured_value("DB_CONNECT_TIMEOUT"),
        )
    except mysql.connector.Error:
        _log_database_failure("initial connection", host, database, active_role)
        raise

    stage = "role activation"
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(f"SET ROLE '{active_role}'@'%'")

            stage = "database selection"
            safe_database = database.replace("`", "``")
            cursor.execute(f"USE `{safe_database}`")
        finally:
            cursor.close()
    except mysql.connector.Error:
        connection.close()
        if has_app_context():
            g.pop("database_connection", None)
        _log_database_failure(stage, host, database, active_role)
        raise

    if has_app_context():
        g.database_connection = connection
        g.database_role = active_role
    return connection


def query(sql, params=(), write=False, role=None):
    connection = get_connection(role=role)
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        if write:
            connection.commit()
            return cursor.lastrowid or cursor.rowcount
        rows = cursor.fetchall()
        for row in rows:
            for name, value in row.items():
                if isinstance(value, timedelta):
                    row[name] = str(value).rjust(8, "0")
        return rows
    except mysql.connector.Error:
        if write:
            connection.rollback()
        raise
    finally:
        cursor.close()


def close_connection(_error=None):
    if not has_app_context():
        return
    connection = g.pop("database_connection", None)
    g.pop("database_role", None)
    if connection is not None:
        connection.close()
