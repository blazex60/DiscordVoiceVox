import asyncio
import os
import discord
from discord.http import Route


def compute_shard_ids(shard_count, cluster_count, cluster_id):
    """このクラスタが担当するシャードIDのリストを返す。
    cluster_count<=1 なら全シャード(=単一プロセス)。"""
    if cluster_count <= 1:
        return list(range(shard_count))
    return [s for s in range(shard_count) if s % cluster_count == cluster_id]


class FastShardedBot(discord.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._identify_semaphore = None
        self._identify_lock = asyncio.Lock()

    async def _get_max_concurrency(self):
        if self._identify_semaphore is not None:
            return self._identify_semaphore
        async with self._identify_lock:
            if self._identify_semaphore is not None:
                return self._identify_semaphore
            data = await self.http.request(Route("GET", "/gateway/bot"))
            mc = data["session_start_limit"]["max_concurrency"]
            print(f"max_concurrency: {mc}")
            self._identify_semaphore = asyncio.Semaphore(mc)
            return self._identify_semaphore

    async def before_identify_hook(self, shard_id, *, initial=False):
        pass

    async def launch_shards(self):
        if self.shard_count is None:
            self.shard_count, gateway = await self.http.get_bot_gateway()
        else:
            gateway = await self.http.get_gateway()

        self._connection.shard_count = self.shard_count

        # クラスタリング: CLUSTER_COUNT>1 のとき担当シャードのみ起動。
        # 未設定 or 1 のときは従来通り全シャードを1プロセスで起動。
        cluster_count = int(os.getenv("CLUSTER_COUNT", "1"))
        cluster_id = int(os.getenv("CLUSTER_ID", "0"))
        if self.shard_ids:
            shard_ids = list(self.shard_ids)
        else:
            shard_ids = compute_shard_ids(self.shard_count, cluster_count, cluster_id)
            if cluster_count > 1:
                print(f"[cluster {cluster_id}/{cluster_count}] shards: {shard_ids}")
        self.shard_ids = shard_ids
        self._connection.shard_ids = shard_ids

        sem = await self._get_max_concurrency()
        mc = sem._value

        for batch_start in range(0, len(shard_ids), mc):
            batch = shard_ids[batch_start:batch_start + mc]
            await asyncio.gather(*(
                self.launch_shard(gateway, sid, initial=(batch_start == 0 and i == 0))
                for i, sid in enumerate(batch)
            ))
            if batch_start + mc < len(shard_ids):
                await asyncio.sleep(5.0)

        self._connection.shards_launched.set()