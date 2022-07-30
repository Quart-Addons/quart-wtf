"""
Test database for async_validators example.
"""
import asyncio

async def db():
    await asyncio.sleep(0.5)
    userdb = {
        'username': 'testpwd',
        'username2': 'testpwd2'
    }
    return userdb

class UserTable():
    async def get_user_by_username(self, username):
        userdb = await db()
        if username:
            return userdb[username]
        raise Exception

get_repo = UserTable()

async def check_username_is_taken(table: UserTable, username: str) -> bool:
    try:
        await table.get_user_by_username(username=username)
    except KeyError:
        return False
    return True
