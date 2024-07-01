from fastapi import HTTPException


def validate_string(input_str: str):
    if not input_str:
        raise HTTPException(status_code=400, detail="Input must be a string")

    if not isinstance(input_str, str):
        raise HTTPException(status_code=400, detail="Input must be a string")

    if not input_str.strip():
        raise HTTPException(status_code=400, detail="Input cannot be empty or just whitespace")
