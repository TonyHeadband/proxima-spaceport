from cryptography.fernet import Fernet

from fastapi import HTTPException, status
from github import Github, BadCredentialsException, UnknownObjectException, Auth

from models.indexer import RepositoryModel, RepoCredentialsModel, NewIndexEntryModel


def get_github_instance_by_token(credentials: RepoCredentialsModel, auth_key: bytes) -> Github:
    try:
        if not credentials.token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="No token found in credentials")
        fernet = Fernet(auth_key)
        decrypted_token = fernet.decrypt(credentials.token).decode('utf-8')
        auth = Auth.Token(decrypted_token)

        gh_instance = Github(auth=auth)
        # Test the credentials by fetching the authenticated user
        gh_instance.get_user()
        return gh_instance
    except BadCredentialsException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid GitHub credentials")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error initializing GitHub instance: {str(e)}")


def get_github_instance(credentials: RepoCredentialsModel, auth_key: bytes) -> Github:
    return get_github_instance_by_token(credentials, auth_key)


def fetch_compose_path(repo: RepositoryModel, credentials: RepoCredentialsModel | None, auth_key: bytes) -> str | None:
    path = f"{repo.compose_folder}docker-compose.yml" if repo.compose_folder else "docker-compose.yml"

    if credentials:
        gh_instance = get_github_instance(credentials, auth_key)
    else:
        gh_instance = Github()

    print(gh_instance.get_repo(repo.name))
    try:
        gh_repo = gh_instance.get_repo(repo.name)
        file_content = gh_repo.get_contents(path, ref=repo.branch)
        return file_content.decoded_content.decode('utf-8')
    except UnknownObjectException:
        print(f"File {path} not found in repository {repo.url}/{repo.branch}")
        return None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error reading file {path} from repository {repo.url}: {str(e)}")


def make_index_entry(repo: RepositoryModel, credentials: RepoCredentialsModel | None, auth_key: bytes) -> NewIndexEntryModel | None:
    compose_content = fetch_compose_path(repo, credentials, auth_key)
    if compose_content is None:
        return None

    return NewIndexEntryModel(repo_id=repo.id, compose_path=compose_content)
