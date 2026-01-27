from motor.motor_asyncio import AsyncIOMotorClient

class Database:
    def __init__(self, uri):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client["ChannelBot"]
        self.maps = self.db["mapping"]

    async def add_mapping(self, source, dest):
        await self.maps.update_one({"source": source}, {"$set": {"dest": dest}}, upsert=True)

    async def get_mapping(self, source):
        res = await self.maps.find_one({"source": source})
        return res["dest"] if res else None
      
