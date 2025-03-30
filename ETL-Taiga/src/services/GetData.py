# %%
import requests
import pandas as pd
from src.services.Auth import auth_taiga
# %%
taiga_host = 'http://209.38.145.133:9000/'
taiga_user = 'taiga-admin'
taiga_password = 'admin'
token = auth_taiga()
# %%
url = f"{taiga_host}/api/v1"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

def fetch_data(endpoint):
    """faz a requisição get para a api do taiga e retorna o json"""
    response = requests.get(f"{url}/{endpoint}", headers=headers)
    if response.status_code == 200:
        try:
            data  = response.json()
            return data if isinstance(data, list) else data['data']
        except requests.exceptions:
            return f"Erro ao fazer a requisição: {response.status_code} - {response.text}"
    else:
        return f"Erro ao fazer a requisição: {response.status_code} - {response.text}"
# %%
# pipeline para gerar dataframes de projetos
def pipeline_projets():
    """pipeline para gerar dataframes de projetos"""
    projects = fetch_data("projects")
    # selecionando apenas os projetos que são da empresa
    campos = ['id', 'name', 'description', 'created_date', 'modified_date']
    projects = pd.DataFrame(projects)[campos].reset_index(drop=True)
    return projects

# %%
def pipeline_roles():
    """pipeline para gerar dataframes de roles"""
    roles = fetch_data("roles")
    campos = ['id', 'name']
    roles = pd.DataFrame(roles)[campos]
    # remover as duplicadas
    roles = roles.drop_duplicates(subset=['name'], keep='first').reset_index(drop=True)
    # resetar o index da coluna id
    roles['id'] = roles.index + 1

    return roles

# %%
# pipeline para gerar dataframes de users
def pipeline_users(roles):
    """Pipeline para gerar dataframes de users com fk_id_role"""
    users = fetch_data("users")
    campos = ['id', 'full_name_display', 'color']

    df_users_input = pd.DataFrame(users)[campos]

    # dict para mapear nome da role
    role_map = dict(zip(roles["name"], roles["id"]))

    # lista com maps de id_user e role
    user_role_map = {}

    for user in users:
        user_id = user['id']
        user_roles = user.get("roles", [])

        for role_name in user_roles:
            if role_name in role_map:
                user_role_map[user_id] = role_map[role_name]
                break

    # Criar a coluna fk_id_role no df_users
    df_users_input["fk_id_role"] = df_users_input["id"].map(user_role_map).fillna(0).astype(int)

    return df_users_input

# %%
# pipeline para gerar dataframes de tags
def pipeline_tags():
    """pipeline para gerar dataframes de user stories"""
    user_stories = fetch_data("userstories")
    campos = ['id', 'tags', 'project']

    # fazer a pipeline para users stories
    # salve = pd.DataFrame(user_stories)

    # pipeline tags de user stories
    tags = pd.DataFrame(user_stories)[campos]
    tags = tags.explode('tags').reset_index(drop=True)
    tags[['name', 'color']] = tags['tags'].apply(pd.Series)
    tags = tags.drop(columns=['tags'])
    tags = tags.rename(columns={'id': 'id_card','project': 'id_project'})
    tags.loc[tags['name'].notna() & tags['color'].isna(), 'color'] = '#a9aabc'
    tags.dropna(inplace=True)
    tags['color'] = tags['color'].str.upper()
    tags['id'] = tags.index + 1

    return tags

# %%
# pipeline para gerar dataframes de status
def pipeline_status():
    """pipeline para gerar dataframes de status"""
    status = fetch_data("userstories")
    campos = ['id', 'status_extra_info','project']

    status = pd.DataFrame(status)[campos]
    status['name'] = status['status_extra_info'].apply(lambda x: x['name'])
    status = status.drop(columns=['status_extra_info'])
    status = status.rename(columns={'id': 'id_card','project': 'id_project'})
    status['id'] = status.index + 1
    return status

# %%
# Executando a pipeline
df_projects = pipeline_projets()
df_roles = pipeline_roles()
df_users = pipeline_users(df_roles)
df_tags= pipeline_tags()
df_status = pipeline_status()
