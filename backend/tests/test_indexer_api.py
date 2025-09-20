def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": 200}


def test_list_and_add_repo(client, api_v1):
    # initially list repos -> empty
    r = client.get(api_v1 + "/repos")
    assert r.status_code == 200
    assert r.json() == []

    # add a repo
    payload = {
        "url": "http://example.com/repo.git",
        "branch": "main",
        "name": "user/repo",
        "compose_folder": "",
        "credentials_name": ""
    }
    r = client.post(api_v1 + "/repos", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "RepositoryModel added successfully"

    # list repos -> should have one
    r = client.get(api_v1 + "/repos")
    assert r.status_code == 200
    repos = r.json()
    assert len(repos) == 1
    assert repos[0]["name"] == "user/repo"


def test_credentials_and_index(client, api_v1):
    cred_payload = {
        "name": "test",
        "username": "u",
        "password": "p",
        "token": ""
    }
    r = client.post(api_v1 + "/credentials", json=cred_payload)
    assert r.status_code == 200
    assert r.json()["message"] == "Credentials added successfully"

    r = client.get(api_v1 + "/credentials")
    assert r.status_code == 200
    creds = r.json()
    assert isinstance(creds, list)

    # updating index on empty repo set should 404
    r = client.post(api_v1 + "/index")
    assert r.status_code == 404

    # add a repo and then re-index
    payload = {
        "url": "http://example.com/repo2.git",
        "branch": "main",
        "name": "user/repo2",
        "compose_folder": "",
        "credentials_name": ""
    }
    r = client.post(api_v1 + "/repos", json=payload)
    assert r.status_code == 200

    # now update index (may succeed or produce 200)
    r = client.post(api_v1 + "/index")
    assert r.status_code in (200,)


def test_edit_and_delete_and_duplicate(client, api_v1):
    # create repo
    payload = {
        "url": "http://example.com/edit.git",
        "branch": "main",
        "name": "user/edit",
        "compose_folder": "",
        "credentials_name": ""
    }
    r = client.post(api_v1 + "/repos", json=payload)
    assert r.status_code == 200

    # fetch repo id
    r = client.get(api_v1 + "/repos")
    repo = r.json()[0]
    repo_id = repo["id"]

    # duplicate create should return 400 (unique constraint)
    r = client.post(api_v1 + "/repos", json=payload)
    assert r.status_code == 400

    # edit repo (change branch)
    edit_payload = {
        "url": repo["url"],
        "branch": "dev",
        "name": repo["name"],
        "compose_folder": repo.get("compose_folder", ""),
        "credentials_name": repo.get("credentials_name", "")
    }
    r = client.put(api_v1 + f"/repos/{repo_id}", json=edit_payload)
    assert r.status_code == 200

    # delete repo
    r = client.delete(api_v1 + f"/repos/{repo_id}")
    assert r.status_code == 200
