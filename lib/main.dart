import 'package:flutter/material.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:provider/provider.dart';
import 'package:tcc_app/models/task_list.dart';
import 'package:tcc_app/pages/chatbot_page.dart';
import 'package:tcc_app/pages/tabs_page.dart';
import 'package:tcc_app/components/task_form.dart';
import 'package:tcc_app/theme/theme_provider.dart';
import 'package:tcc_app/utils/app_routes.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Future.wait([
  ]);
  await initializeDateFormatting('pt_BR', null);
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  @override
  void initState() {
    super.initState();
    ThemeProvider();
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider<TaskList>(create: (_) => TaskList()),
        ChangeNotifierProvider<ThemeProvider>(create: (_) => ThemeProvider()),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, _) {
          return MaterialApp(
            title: 'Tasks',
            theme: themeProvider.themeData,
            routes: {
              AppRoutes.home: (ctx) => const TabsScreen(),
              AppRoutes.taskForm: (ctx) => const TaskForm(),
              AppRoutes.chatBot: (ctx) => ChatbotScreen(),
            },
            debugShowCheckedModeBanner: false,
          );
        },
      ),
    );
  }
}
