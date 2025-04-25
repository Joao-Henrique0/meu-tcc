import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:tcc_app/components/notification.dart';
import 'package:tcc_app/models/task_list.dart';
import 'package:tcc_app/pages/chatbot_page.dart';
import 'package:tcc_app/pages/tabs_page.dart';
import 'package:tcc_app/components/task_form.dart';
import 'package:tcc_app/theme/theme_provider.dart';
import 'package:tcc_app/utils/app_routes.dart';
import 'package:timezone/data/latest_all.dart' as tz;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  // await FirebaseNotificationService.init();
  tz.initializeTimeZones();
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
    requestNotificationPermissions();
    setupFirebaseMessaging();
    getToken();
  }

  Future<void> requestNotificationPermissions() async {
    FirebaseMessaging messaging = FirebaseMessaging.instance;

    NotificationSettings settings = await messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print("Permissão concedida!");
    } else {
      print("Permissão negada.");
    }
  }

  void setupFirebaseMessaging() {
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print("Nova notificação: ${message.notification?.title}");
      // Aqui você pode exibir um alerta ou outra ação
    });
  }

  Future<void> getToken() async {
    String? token = await FirebaseMessaging.instance.getToken();
    print("Token do dispositivo: $token");
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
