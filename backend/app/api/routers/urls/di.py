from fastapi import Header, HTTPException, status

__all__ = ("get_user_id",)


async def get_user_id(x_user_id: str = Header(...)) -> str:
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required",
        )
    return x_user_id
