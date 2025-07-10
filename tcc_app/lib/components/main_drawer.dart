import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:provider/provider.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:tcc_app/models/task_list.dart';
import 'package:tcc_app/theme/theme.dart';
import 'package:tcc_app/theme/theme_provider.dart';

class MainDrawer extends StatelessWidget {
  const MainDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    final user = Supabase.instance.client.auth.currentUser;

    return Drawer(
      child: Column(
        children: [
          AppBar(title: const Text('Opções'), automaticallyImplyLeading: false),
          ListTile(
            leading: const Icon(Icons.brightness_6),
            title: const Text('Modo Escuro'),
            trailing: Consumer<ThemeProvider>(
              builder: (context, themeProvider, _) {
                return Switch(
                  value: themeProvider.themeData == darkMode,
                  onChanged: (val) {
                    themeProvider.toggleTheme();
                  },
                );
              },
            ),
          ),
          ListTile(
            leading: const Icon(Icons.notifications),
            title: const Text('Configurações de Notificação'),
            onTap: () {
              Navigator.pushNamed(context, '/noti-settings');
            },
          ),
          ListTile(
            leading: const Icon(Icons.cloud_download),
            title: const Text('Restaurar backup'),
            onTap: () async {
              final taskList = Provider.of<TaskList>(context, listen: false);
              // Salve o contexto do ScaffoldMessenger ANTES do pop!
              final scaffoldMessenger = ScaffoldMessenger.maybeOf(context);

              Navigator.of(context).pop();

              await taskList.restoreTasksFromSupabase();

              // Agora use o contexto salvo, que ainda é válido!
              if (scaffoldMessenger != null) {
                scaffoldMessenger.showSnackBar(
                  const SnackBar(content: Text('Backup restaurado!')),
                );
              }
            },
          ),
          ListTile(
            leading: Icon(user != null ? Icons.cloud_done : Icons.login),
            title: Text(
              user != null
                  ? 'Backup ativo e ChatBot conectado'
                  : 'Login para Backup e ChatBot',
            ),
            onTap: () async {
              if (user != null) {
                await showDialog(
                  context: context,
                  builder:
                      (ctx) => AlertDialog(
                        title: const Text('Já está logado'),
                        content: const Text('Deseja sair da conta?'),
                        actions: [
                          TextButton(
                            onPressed:
                                () => Navigator.of(ctx).pop(), // Fecha o dialog
                            child: const Text('Cancelar'),
                          ),
                          TextButton(
                            onPressed: () async {
                              Navigator.of(ctx).pop(); // Fecha o dialog
                              await Supabase.instance.client.auth.signOut(
                                scope: SignOutScope.global,
                              );
                              await GoogleSignIn().signOut(); // Se usar Google
                              Navigator.of(context).pushReplacementNamed('/');
                            },
                            child: const Text('Logout'),
                          ),
                        ],
                      ),
                );
              } else {
                Navigator.of(context).pushNamed('/login');
              }
            },
          ),
        ],
      ),
    );
  }
}
