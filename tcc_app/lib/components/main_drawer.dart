import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tcc_app/theme/theme.dart';
import 'package:tcc_app/theme/theme_provider.dart';

class MainDrawer extends StatelessWidget {
  const MainDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: Column(
        children: [
          AppBar(
            title: const Text('Opções'),
            automaticallyImplyLeading: false,
          ),
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
        ],
      ),
    );
  }
}
