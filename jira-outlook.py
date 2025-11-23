import requests
from requests.auth import HTTPBasicAuth
import msal
import os
import json

# ===============================
# CONFIG JIRA
# ===============================
JIRA_EMAIL = "instalacionesgian@gmail.com"
JIRA_TOKEN = "ATATT3xFfGF0j5R04LDOeD6LbXvuD2_7SE88PoORiSYd56sIzpgZsarSuepdWBS9lGw5t_DWPFuGk4ltmAajiW5O-xW5MhQplRdUQIz-4g3LW4GiEH9j0W3v0LccPNw81PHYu_xJW43rhtPGyWmUglNk8h84Fb17UXlHcInp7SpfzNaAQqjOc30=A681F68A"
JIRA_DOMAIN = "instalacionesgian.atlassian.net"
PROJECT_KEY = "IN"

# ===============================
# CONFIG MICROSOFT GRAPH
# ===============================
CLIENT_ID = "78a15de9-dd50-4d2a-b4a8-564797a3b6a0"
TENANT_ID = "common"
SCOPES = ["Mail.Send"]
TO_EMAIL = "instalacionesgian@gmail.com"

# ===============================
# CAMPOS CUSTOM DE JIRA
# ===============================
CUSTOM_FIELDS = {
    "SystemID": "customfield_10171",
    "BranchID": "customfield_10172",
    "BranchName": "customfield_10173",
    "ClientAppID": "customfield_10174",
    "ClientAppName": "customfield_10175",
    "TerminalID": "customfield_10168",
    "RUT": "customfield_10167"
}

# ===============================
# FUNCIONES JIRA
# ===============================
def get_issue_ids():
    print("📥 Consultando Jira...")
    url = f"https://{JIRA_DOMAIN}/rest/api/3/search/jql"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    # SOLO issues que estén en To Do
    payload = {
        "jql": f'project = "{PROJECT_KEY}" AND status = "To Do" ORDER BY created DESC',
        "maxResults": 50
    }
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers, auth=auth)
    if r.status_code != 200:
        print("❌ ERROR:", r.text)
        return []
    data = r.json()
    return [issue["id"] for issue in data.get("issues", [])]


def get_issue_fields(issue_id):
    url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_id}"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    headers = {"Accept": "application/json"}
    r = requests.get(url, headers=headers, auth=auth)
    if r.status_code != 200:
        print(f"❌ Error obteniendo fields del issue {issue_id}: {r.text}")
        return None
    return r.json()["fields"]

def transition_issue(issue_id, transition_id):
    """Mueve el issue a la transición indicada"""
    url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/{issue_id}/transitions"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {"transition": {"id": transition_id}}
    r = requests.post(url, headers=headers, auth=auth, json=payload)
    if r.status_code == 204:
        print(f"✅ Issue {issue_id} movido correctamente a la transición {transition_id}")
    else:
        print(f"❌ Error moviendo issue {issue_id}: {r.status_code} {r.text}")

# ===============================
# AUTENTICACIÓN MSAL CON CACHE
# ===============================
CACHE_FILE = "token_cache.bin"

def get_access_token():
    from msal import SerializableTokenCache
    cache = SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        cache.deserialize(open(CACHE_FILE, "r").read())

    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        token_cache=cache
    )

    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]

    # Si no hay token válido, iniciar Device Code Flow
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise ValueError("No se pudo crear el flujo de dispositivo")
    print(flow["message"])
    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        # Guardar cache de tokens
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())
        return result["access_token"]
    else:
        raise ValueError(f"No se obtuvo token: {result.get('error_description')}")

# ===============================
# ENVIAR MAIL POR GRAPH
# ===============================
def send_mail_graph(subject, body, access_token):
    url = "https://graph.microsoft.com/v1.0/me/sendMail"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [{"emailAddress": {"address": TO_EMAIL}}]
        }
    }
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 202:
        print("✅ Mail enviado con éxito")
        return True
    else:
        print(f"❌ Error al enviar mail: {r.status_code} {r.text}")
        return False

# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    access_token = get_access_token()
    issue_ids = get_issue_ids()

    if not issue_ids:
        print("⚠️ No tenemos ninguna issue en estado 'To Do'.")
    else:
        print("🔍 Issues:", issue_ids)

        for iid in issue_ids:
            fields = get_issue_fields(iid)
            if not fields:
                continue

            razon_social = fields.get("summary", "")
            rut = fields.get(CUSTOM_FIELDS["RUT"], "")
            sys_id = fields.get(CUSTOM_FIELDS["SystemID"], "")
            branch_id = fields.get(CUSTOM_FIELDS["BranchID"], "")
            branch_name = fields.get(CUSTOM_FIELDS["BranchName"], "")
            client_app_id = fields.get(CUSTOM_FIELDS["ClientAppID"], "")
            client_app_name = fields.get(CUSTOM_FIELDS["ClientAppName"], "")
            terminal_id = fields.get(CUSTOM_FIELDS["TerminalID"], "")

            asunto = f"Nueva Instalación - {razon_social} RUT: {rut} - OCA"
            cuerpo = f"""
Estimados, buenos días. Espero que se encuentren bien.

Envío los datos del nuevo cliente nombrado en el asunto para la integración de su terminal OCA:

System ID: {sys_id}
Branch ID: {branch_id}
Branch Name: {branch_name}
Client App ID: {client_app_id}
Client App Name: {client_app_name}
Terminal ID: {terminal_id}

De nuestra parte, la terminal ya fue enviada preconfigurada, por lo que no requiere modificaciones de configuración. En caso de presentarse algún error durante la integración, por favor contáctense con nosotros para asistir de inmediato.

Quedo a las órdenes.
Muchas gracias.
Saludos.
"""
            # Enviar mail
            if send_mail_graph(asunto, cuerpo, access_token):
                # Si se envió correctamente, mover a EN INTEGRADOR (ID = 2)
                transition_issue(iid, "2")
