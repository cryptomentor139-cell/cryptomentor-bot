"""
Supabase client wrapper untuk Marketing AI Agent.
marketing/agent/db/supabase_client.py
"""
from __future__ import annotations

from typing import Any

from supabase import Client, create_client

from marketing.agent.config import Config


class SupabaseDB:
    """
    Thin async wrapper di atas Supabase Python client.

    Contoh penggunaan:
        db = SupabaseDB(config)
        row  = await db.insert("marketing_campaigns", {"cycle_number": 1})
        rows = await db.select("marketing_content", filters={"status": "approved"})
        row  = await db.update("marketing_leads", lead_id, {"segment": "Hot"})
        row  = await db.upsert("marketing_audience_personas", {...})
    """

    def __init__(self, config: Config) -> None:
        self.client: Client = create_client(config.supabase_url, config.supabase_key)

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    async def insert(self, table: str, data: dict[str, Any]) -> dict[str, Any]:
        """Insert satu baris ke tabel. Return baris yang baru dibuat."""
        response = self.client.table(table).insert(data).execute()
        return response.data[0]

    async def update(self, table: str, id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update baris berdasarkan primary key `id`. Return baris yang diperbarui."""
        response = (
            self.client.table(table)
            .update(data)
            .eq("id", id)
            .execute()
        )
        return response.data[0]

    async def select(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Select baris dari tabel dengan filter opsional.

        `filters` adalah dict key=value yang di-AND-kan sebagai equality filter.
        Contoh: {"status": "approved", "platform": "instagram"}
        """
        query = self.client.table(table).select("*").limit(limit)
        if filters:
            for column, value in filters.items():
                query = query.eq(column, value)
        response = query.execute()
        return response.data

    async def upsert(self, table: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Upsert satu baris (insert atau update jika sudah ada berdasarkan PK).
        Return baris hasil upsert.
        """
        response = self.client.table(table).upsert(data).execute()
        return response.data[0]
