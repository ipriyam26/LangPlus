"""Mastodon document loader."""
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Sequence

from langplus.docstore.document import Document
from langplus.document_loaders.base import BaseLoader

if TYPE_CHECKING:
    import mastodon


def _dependable_mastodon_import() -> mastodon:
    try:
        import mastodon
    except ImportError:
        raise ValueError(
            "Mastodon.py package not found, "
            "please install it with `pip install Mastodon.py`"
        )
    return mastodon


class MastodonTootsLoader(BaseLoader):
    """Mastodon toots loader."""

    def __init__(
        self,
        mastodon_accounts: Sequence[str],
        number_toots: Optional[int] = 100,
        exclude_replies: bool = False,
        access_token: Optional[str] = None,
        api_base_url: str = "https://mastodon.social",
    ):
        """Instantiate Mastodon toots loader.

        Args:
            mastodon_accounts: The list of Mastodon accounts to query.
            number_toots: How many toots to pull for each account.
            exclude_replies: Whether to exclude reply toots from the load.
            access_token: An access token if toots are loaded as a Mastodon app. Can
                also be specified via the environment variables "MASTODON_ACCESS_TOKEN".
            api_base_url: A Mastodon API base URL to talk to, if not using the default.
        """
        mastodon = _dependable_mastodon_import()
        access_token = access_token or os.environ.get("MASTODON_ACCESS_TOKEN")
        self.api = mastodon.Mastodon(
            access_token=access_token, api_base_url=api_base_url
        )
        self.mastodon_accounts = mastodon_accounts
        self.number_toots = number_toots
        self.exclude_replies = exclude_replies

    def load(self) -> List[Document]:
        """Load toots into documents."""
        results: List[Document] = []
        for account in self.mastodon_accounts:
            user = self.api.account_lookup(account)
            toots = self.api.account_statuses(
                user.id,
                only_media=False,
                pinned=False,
                exclude_replies=self.exclude_replies,
                exclude_reblogs=True,
                limit=self.number_toots,
            )
            docs = self._format_toots(toots, user)
            results.extend(docs)
        return results

    def _format_toots(
        self, toots: List[Dict[str, Any]], user_info: dict
    ) -> Iterable[Document]:
        """Format toots into documents.

        Adding user info, and selected toot fields into the metadata.
        """
        for toot in toots:
            metadata = {
                "created_at": toot["created_at"],
                "user_info": user_info,
                "is_reply": toot["in_reply_to_id"] is not None,
            }
            yield Document(
                page_content=toot["content"],
                metadata=metadata,
            )
