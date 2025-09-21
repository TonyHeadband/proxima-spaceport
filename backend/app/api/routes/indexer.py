from fastapi import APIRouter, HTTPException, Depends, status
from dependencies import get_db, get_cryptography_key

from sqlalchemy.orm import Session

from models.indexer import IndexerResponseModel, RepositoryModel
from models.indexer import CreateNewRepoModel, RepoCredentialsModel, NewRepoCredentialsModel

from services.indexer import create_new_repo, list_repositories, update_repo
from services.indexer import create_new_credentials, get_all_credentials
from services.indexer import get_index_values, rescan_index_values

from database import Repos

router = APIRouter()


@router.post(
    "/repos",
    name="indexer:add-repo",
)
async def add_repo(new_repo: CreateNewRepoModel, db: Session = Depends(get_db)) -> IndexerResponseModel:
    """
    Add a new repository to be indexed.
    """
    try:
        await create_new_repo(new_repo.url, new_repo.branch,
                              new_repo.name, new_repo.compose_folder, new_repo.credentials_name, db)
    except HTTPException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)

    return IndexerResponseModel(status=status.HTTP_200_OK, message="RepositoryModel added successfully")


@router.put(
    "/repos/{repo_id}",
    name="indexer:edit-repo",
)
async def edit_repo(repo_id: str, repo: CreateNewRepoModel, db: Session = Depends(get_db)) -> RepositoryModel:
    """
    Edit an existing repository to be indexed.

    """
    existing_repo = db.query(Repos).filter(Repos.id == repo_id).first()
    if not existing_repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="RepositoryModel not found")

    update_data = repo.model_dump()
    for key, value in update_data.items():
        if hasattr(existing_repo, key):
            setattr(existing_repo, key, value)

    try:
        await update_repo(existing_repo, db)
    except HTTPException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)

    return RepositoryModel(**existing_repo.as_dict())


@router.delete(
    "/repos/{repo_id}",
    name="indexer:delete-repo",
)
async def delete_repo(repo_id: str, db: Session = Depends(get_db)) -> IndexerResponseModel:
    """
    Delete a repository from the index.
    """
    # fetch ORM instance directly for deletion
    existing_repo = db.query(Repos).filter(Repos.id == repo_id).first()
    if not existing_repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="RepositoryModel not found")

    try:
        db.delete(existing_repo)
        db.commit()
    except HTTPException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)

    return IndexerResponseModel(status=status.HTTP_200_OK, message="RepositoryModel deleted successfully")


@router.get(
    "/repos",
    name="indexer:list-repos",
)
async def list_repos(db: Session = Depends(get_db)) -> list[RepositoryModel]:
    """
    List all indexed repositories.
    """
    repos: list[RepositoryModel] = await list_repositories(db)
    return repos


@router.post(
    "/credentials",
    name="indexer:add-credentials",
)
async def add_credentials(credentials: NewRepoCredentialsModel, db: Session = Depends(get_db), auth_key: bytes = Depends(get_cryptography_key)) -> IndexerResponseModel:
    """
    Add new credentials for accessing private repositories.
    """

    if not credentials.name:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Name is required")
    if not credentials.username:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="username is required")
    if not (credentials.password or credentials.token):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Password or token is required")

    try:
        await create_new_credentials(
            credentials.name, credentials.username, credentials.password, credentials.token, db, auth_key)
    except HTTPException as exc:
        raise exc

    return IndexerResponseModel(status=status.HTTP_200_OK, message="Credentials added successfully")


@router.get(
    "/credentials",
    name="indexer:get-credentials",
)
async def get_credentials(db: Session = Depends(get_db)) -> list[RepoCredentialsModel]:
    """
    List all stored credentials.
    """
    creds: list[RepoCredentialsModel] = await get_all_credentials(db)
    return creds


@router.get(
    "/index",
    name="indexer:get-index",
)
async def get_index(db: Session = Depends(get_db)) -> list[dict[str, str | None]]:
    """
    Get indexing information for a specific repository.
    """
    try:
        values: list[dict[str, str | None]] = await get_index_values(db)
    except HTTPException as exc:
        raise exc

    return values


@router.post(
    "/index",
    name="indexer:update-index",
)
async def update_index(force: bool = False, db: Session = Depends(get_db), auth_key: bytes = Depends(get_cryptography_key)) -> IndexerResponseModel:
    """
    Trigger re-indexing of all repositories. the force parameter is not used at the moment.
    """
    if db.query(Repos).count() == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No repositories found to index.")
    if force:
        message = "Re-indexing triggered with force."
    else:
        message = "Re-indexing triggered."

    try:
        await rescan_index_values(force, db, auth_key)
    except HTTPException as exc:
        raise exc

    return IndexerResponseModel(status=status.HTTP_200_OK, message=message)
