// import 'dart:async';
// import 'package:flutter_local_notifications/flutter_local_notifications.dart';
// import 'package:firebase_messaging/firebase_messaging.dart';
// import 'package:flutter_timezone/flutter_timezone.dart';
// import 'package:timezone/data/latest_all.dart' as tz;
// import 'package:timezone/timezone.dart' as tz;

// class FirebaseNotificationService {
//   static FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
//       FlutterLocalNotificationsPlugin();
//   static StreamController<NotificationResponse> streamController =
//       StreamController();

//   static Future<void> init() async {
//     const AndroidInitializationSettings androidInit =
//         AndroidInitializationSettings('@mipmap/ic_launcher');
//     const InitializationSettings settings =
//         InitializationSettings(android: androidInit);

//     await flutterLocalNotificationsPlugin.initialize(
//       settings,
//       onDidReceiveNotificationResponse: (response) {
//         streamController.add(response);
//       },
//       onDidReceiveBackgroundNotificationResponse: (response) {
//         streamController.add(response);
//       },
//     );

//     FirebaseMessaging messaging = FirebaseMessaging.instance;
//     await messaging.requestPermission();

//     String? token = await messaging.getToken();
//     print("Token do dispositivo: $token");

//     FirebaseMessaging.onMessage.listen((RemoteMessage message) {
//       showInstantNotification(
//         message.notification?.title ?? "Nova Notificação",
//         message.notification?.body ?? "Você recebeu uma nova notificação",
//       );
//     });

//     FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
//       print("Usuário abriu a notificação: ${message.notification?.title}");
//     });
//   }

//   // 🔹 Notificação Local Agendada para Tarefas
//   static void scheduleNotification(
//       String title, String description, DateTime taskTime, String id) async {
//     const AndroidNotificationDetails android = AndroidNotificationDetails(
//       'scheduled_notification',
//       'Task Notification',
//       importance: Importance.max,
//       priority: Priority.high,
//       icon: '@mipmap/ic_launcher',
//       enableVibration: true,
//     );

//     const NotificationDetails details = NotificationDetails(android: android);

//     tz.initializeTimeZones();
//     final String currentTimeZone = await FlutterTimezone.getLocalTimezone();
//     tz.setLocalLocation(tz.getLocation(currentTimeZone));

//     var scheduleTime = tz.TZDateTime.from(taskTime, tz.local)
//         .subtract(const Duration(minutes: 10));

//     if (scheduleTime.isBefore(tz.TZDateTime.now(tz.local))) {
//       return;
//     }

//     await flutterLocalNotificationsPlugin.zonedSchedule(
//       int.parse(id),
//       'Tarefa: $title',
//       description,
//       scheduleTime,
//       details,
//       matchDateTimeComponents: DateTimeComponents.time, androidScheduleMode: AndroidScheduleMode.exact,
//     );
//   }

//   // 🔹 Exibir Notificação Instantânea (Para Firebase)
//   static void showInstantNotification(String title, String body) async {
//     const AndroidNotificationDetails android = AndroidNotificationDetails(
//       'firebase_notification',
//       'Firebase Notifications',
//       importance: Importance.max,
//       priority: Priority.high,
//       icon: '@mipmap/ic_launcher',
//       enableVibration: true,
//     );

//     const NotificationDetails details = NotificationDetails(android: android);

//     await flutterLocalNotificationsPlugin.show(
//       0,
//       title,
//       body,
//       details,
//     );
//   }

//   static void cancelNotification(int id) async {
//     await flutterLocalNotificationsPlugin.cancel(id);
//   }
// }
