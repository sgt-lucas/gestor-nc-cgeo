import flet as ft
from supabase_client import supabase  # Importa o nosso cliente
from supabase_auth.errors import AuthApiError

# Importa as nossas novas "views" (abas)
from views.dashboard_view import create_dashboard_view
from views.ncs_view import create_ncs_view
from views.nes_view import create_nes_view
from views.relatorios_view import create_relatorios_view
from views.admin_view import create_admin_view

def main(page: ft.Page):
    
    page.title = "GESTÃO DE NOTAS DE CRÉDITO - 2º CGEO"
    
    # --- DEV MODE: Definir utilizador padrão (para saltar login) ---
    page.session.set("user_email", "desenvolvimento@local")
    # UUID falso - pode ser qualquer um no formato correto
    page.session.set("user_id", "11111111-1111-1111-1111-111111111111") 
    page.session.set("user_funcao", "admin") # Defina como "admin" para ver todas as abas
    # --- FIM DEV MODE ---
    
    # Define o tema com as cores corretas (strings)
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="green800",
            primary_container="green900",
            background="grey100",
            surface="white",
        )
    )

    # --- Campos de Login (Inalterados) ---
    email_field = ft.TextField(
        label="E-mail", 
        prefix_icon="EMAIL",
        width=350,
        keyboard_type=ft.KeyboardType.EMAIL,
        value="@dominio.com" 
    )
    password_field = ft.TextField(
        label="Senha", 
        prefix_icon="LOCK", 
        width=350,
        password=True, 
        can_reveal_password=True
    )

    def show_main_layout(e=None):
        """ 
        Constrói a interface principal da aplicação (Abas) após o login.
        """
        page.clean() # Limpa a tela de login
        page.vertical_alignment = ft.MainAxisAlignment.START # Reseta o alinhamento

        # --- Criar a Barra Superior (AppBar) ---
        page.appbar = ft.AppBar(
            title=ft.Text("Gestor NC/NE - 2º CGEO"),
            bgcolor="green800",
            color="white",
            actions=[
                ft.Text(f"Utilizador: {page.session.get('user_email')}"),
                ft.IconButton(
                    icon="LOGOUT",
                    tooltip="Sair",
                    on_click=handle_logout,
                    icon_color="white"
                )
            ]
        )

        # --- Carregar o conteúdo de cada aba ---
        view_dashboard = create_dashboard_view(page)
        view_ncs = create_ncs_view(page)
        view_nes = create_nes_view(page)
        view_relatorios = create_relatorios_view(page)
        
        # --- Criar as Abas ---
        abas_principais = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            expand=True,
            tabs=[
                ft.Tab(
                    text="Dashboard",
                    icon="DASHBOARD",
                    content=view_dashboard
                ),
                ft.Tab(
                    text="Notas de Crédito",
                    icon="PAYMENT",
                    content=view_ncs
                ),
                ft.Tab(
                    text="Notas de Empenho",
                    icon="RECEIPT",
                    content=view_nes
                ),
                ft.Tab(
                    text="Relatórios",
                    icon="PRINT",
                    content=view_relatorios
                ),
            ]
        )
        
        # --- LÓGICA DE ADMIN ---
        # Verifica a função que guardámos na sessão
        if page.session.get("user_funcao") == "admin":
            view_admin = create_admin_view(page)
            abas_principais.tabs.append(
                ft.Tab(
                    text="Administração",
                    icon="ADMIN_PANEL_SETTINGS",
                    content=view_admin
                )
            )

        page.add(abas_principais)
        page.update()

    def handle_login(e):
        """Tenta fazer login com o Supabase."""
        email = email_field.value
        password = password_field.value

        if not email or not password:
            show_snackbar("Preencha todos os campos.")
            return

        try:
            # 1. Tentar fazer o login
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            user = auth_response.user
            page.session.set("user_email", user.email)
            page.session.set("user_id", user.id)
            page.session.set("access_token", auth_response.session.access_token)

            supabase.auth.set_session(
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token
            )
            
            # --- NOVO: Buscar a Função (Role) do Utilizador ---
            try:
                # Buscamos o perfil do usuário logado na nossa tabela 'perfis_usuarios'
                resposta_perfil = supabase.table('perfis_usuarios') \
                                          .select('funcao') \
                                          .eq('id_usuario', user.id) \
                                          .single() \
                                          .execute()
                
                funcao = resposta_perfil.data['funcao']
                page.session.set("user_funcao", funcao) # Guardamos a função na sessão
                print(f"Login OK: {user.email} (Função: {funcao})")
                
            except Exception as ex_perfil:
                # Se falhar (ex: perfil não encontrado, o que não deve acontecer)
                print(f"Erro ao buscar perfil: {ex_perfil}")
                show_snackbar(f"Erro ao carregar perfil de utilizador: {ex_perfil}")
                return
            # --- FIM DA PARTE NOVA ---

            # 2. Mostrar a aplicação principal
            show_main_layout()

        except AuthApiError as ex:
            print(f"Erro de Login: {ex.message}")
            show_snackbar(f"Erro: {ex.message}")
        except Exception as ex:
            print(f"Erro inesperado: {ex}")
            show_snackbar("Ocorreu um erro inesperado.")
            
    def handle_register(e):
        """Tenta registar um novo utilizador."""
        email = email_field.value
        password = password_field.value

        if not email or not password:
            show_snackbar("Preencha todos os campos para registar.")
            return

        try:
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            print(f"Registo OK: {auth_response.user.email}")
            show_snackbar("Registo bem-sucedido! Faça o login agora.", "green")

        except AuthApiError as ex:
            print(f"Erro de Registo: {ex.message}")
            show_snackbar(f"Erro ao registar: {ex.message}")
        except Exception as ex:
            print(f"Erro inesperado: {ex}")
            show_snackbar("Ocorreu um erro inesperado.")

    def handle_logout(e):
        """Limpa a sessão e volta para a tela de login."""
        page.session.clear()
        page.appbar = None # Remove a barra superior
        page.clean()
        
        # Reconstrói a tela de login
        page.vertical_alignment = ft.MainAxisAlignment.CENTER 
        page.add(build_login_view())
        page.update()


    def show_snackbar(message, color="red"):
        """Mostra uma mensagem de feedback."""
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()


    def build_login_view():
        """Constrói a tela de login inicial."""
        # Alinha a tela de login ao centro
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        
        return ft.Column(
            [
                ft.Text("Gestor NC/NE", size=32, weight=ft.FontWeight.BOLD),
                ft.Text("Controlo Orçamentário - 2º CGEO", size=16),
                ft.Container(height=30), # Espaçador
                email_field,
                password_field,
                ft.Container(height=10), # Espaçador
                ft.Row(
                    [
                        ft.ElevatedButton("Login", on_click=handle_login, expand=True, icon="LOGIN"),
                        ft.OutlinedButton("Registar", on_click=handle_register, expand=True, icon="PERSON_ADD"),
                    ],
                    width=350
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

    # --- Estado Inicial ---
# (DEV MODE: Saltar login e ir direto para a app principal)
# page.add(build_login_view()) # Comenta a linha antiga
    show_main_layout()            # Chama diretamente a função que constrói as abas


# --- Executar a Aplicação ---
if __name__ == "__main__":
    ft.app(
        target=main, 
        view=ft.AppView.FLET_APP, # Faz parecer uma app desktop
        assets_dir="assets" 
    )