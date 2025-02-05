import os
from typing import Callable, List, Optional

from langplus.docstore.document import Document
from langplus.document_loaders.base import BaseLoader


class GitLoader(BaseLoader):
    """Loads files from a Git repository into a list of documents.
    Repository can be local on disk available at `repo_path`,
    or remote at `clone_url` that will be cloned to `repo_path`.
    Currently supports only text files.

    Each document represents one file in the repository. The `path` points to
    the local Git repository, and the `branch` specifies the branch to load
    files from. By default, it loads from the `main` branch.
    """

    def __init__(
        self,
        repo_path: str,
        clone_url: Optional[str] = None,
        branch: Optional[str] = "main",
        file_filter: Optional[Callable[[str], bool]] = None,
    ):
        self.repo_path = repo_path
        self.clone_url = clone_url
        self.branch = branch
        self.file_filter = file_filter

    def load(self) -> List[Document]:
        try:
            from git import Blob, Repo  # type: ignore
        except ImportError as ex:
            raise ImportError(
                "Could not import git python package. "
                "Please install it with `pip install GitPython`."
            ) from ex

        if not os.path.exists(self.repo_path) and self.clone_url is None:
            raise ValueError(f"Path {self.repo_path} does not exist")
        elif self.clone_url:
            repo = Repo.clone_from(self.clone_url, self.repo_path)
            repo.git.checkout(self.branch)
        else:
            repo = Repo(self.repo_path)
            repo.git.checkout(self.branch)

        docs: List[Document] = []

        for item in repo.tree().traverse():
            if not isinstance(item, Blob):
                continue

            file_path = os.path.join(self.repo_path, item.path)

            ignored_files = repo.ignored([file_path])  # type: ignore
            if len(ignored_files):
                continue

            # uses filter to skip files
            if self.file_filter and not self.file_filter(file_path):
                continue

            rel_file_path = os.path.relpath(file_path, self.repo_path)
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                    file_type = os.path.splitext(item.name)[1]

                    # loads only text files
                    try:
                        text_content = content.decode("utf-8")
                    except UnicodeDecodeError:
                        continue

                    metadata = {
                        "source": rel_file_path,
                        "file_path": rel_file_path,
                        "file_name": item.name,
                        "file_type": file_type,
                    }
                    doc = Document(page_content=text_content, metadata=metadata)
                    docs.append(doc)
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

        return docs
