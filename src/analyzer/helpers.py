# helpers.py
from typing import Any, Optional
import typer

def PathOption(
    flag: str,
    help: Optional[str] = None,
    *,
    exists: Optional[bool] = None,
    file_okay: Optional[bool] = None,
    dir_okay: Optional[bool] = None,
    readable: Optional[bool] = None,
    writable: Optional[bool] = None,
    resolve_path: Optional[bool] = None,
    allow_dash: Optional[bool] = None,
) -> Any:
    return typer.Option(
        flag,
        help=help,
        exists=exists,
        file_okay=file_okay,
        dir_okay=dir_okay,
        readable=readable,
        writable=writable,
        resolve_path=resolve_path,
        allow_dash=allow_dash,
    )
