import 'dart:async';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:timezone/data/latest_all.dart' as tz;
import 'package:timezone/timezone.dart' as tz;
import 'package:shared_preferences/shared_preferences.dart';

typedef TaskCompleteCallback =
    Future<void> Function(String taskId, bool complete);

class LocalNotificationService {
  static final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();
  static final StreamController<NotificationResponse> streamController =
      StreamController.broadcast();

  static final Map<String, String> _taskIdMap = {}; // taskId → taskId
  static TaskCompleteCallback? _onTaskComplete;

  static void registerOnTaskComplete(TaskCompleteCallback callback) {
    _onTaskComplete = callback;
  }

  static Future<void> onTap(NotificationResponse notificationResponse) async {
    print("Notificação clicada ou ação: ${notificationResponse.actionId}");

    final payload = notificationResponse.payload;

    // Caso seja o botão de ação
    if (notificationResponse.actionId == 'concluir_tarefa') {
      // Extrair o taskId do payload
      if (payload != null && payload.startsWith("concluir|")) {
        final parts = payload.split("|");
        if (parts.length >= 2) {
          final taskId = parts[1];
          print("Concluir tarefa: $taskId");

          if (_taskIdMap.containsKey(taskId)) {
            await _onTaskComplete?.call(taskId, true); // Marcar como concluída
            await cancelNotification(taskId.hashCode);
            _taskIdMap.remove(taskId);
          }
        }
      }
    } else {
      // Caso o usuário clique na notificação inteira (não no botão)
      print("Usuário clicou na notificação em si.");
    }
  }

  static Future<void> init() async {
    const androidInit = AndroidInitializationSettings('@mipmap/ic_launcher');
    const settings = InitializationSettings(android: androidInit);

    await flutterLocalNotificationsPlugin.initialize(
      settings,
      onDidReceiveNotificationResponse: onTap,
      onDidReceiveBackgroundNotificationResponse: onTap,
    );

    // Solicita permissão para notificações (Android 13+)
    await flutterLocalNotificationsPlugin
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.requestNotificationsPermission();
  }

  static Future<void> showScheduledRepeatingNotification({
    required String title,
    required String description,
    required DateTime taskTime,
    required String taskId,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final firstMinutes = prefs.getInt('first_notification') ?? 30;
    final repeatMinutes = prefs.getInt('repeat_interval') ?? 20;

    tz.initializeTimeZones();
    final currentTimeZone = await FlutterTimezone.getLocalTimezone();
    tz.setLocalLocation(tz.getLocation(currentTimeZone));

    final firstNotificationTime = tz.TZDateTime.from(
      taskTime,
      tz.local,
    ).subtract(Duration(minutes: firstMinutes));

    if (firstNotificationTime.isBefore(tz.TZDateTime.now(tz.local))) {
      print("Horário inválido para agendamento.");
      return;
    }

    final notificationId = taskId.hashCode;
    _taskIdMap[taskId] = taskId;

    const androidDetails = AndroidNotificationDetails(
      'scheduled_repeating_channel',
      'Notificações Repetitivas',
      channelDescription:
          'Notificações que se repetem até a tarefa ser concluída',
      importance: Importance.max,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
      enableVibration: true,
      actions: <AndroidNotificationAction>[
        AndroidNotificationAction(
          'concluir_tarefa',
          'Concluir Tarefa',
          showsUserInterface: true,
          cancelNotification: true,
        ),
      ],
    );

    final details = NotificationDetails(android: androidDetails);

    await flutterLocalNotificationsPlugin.zonedSchedule(
      notificationId,
      'Tarefa: $title',
      description,
      firstNotificationTime,
      details,
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      payload: 'concluir|$taskId',
    );

    // Repetir manualmente com Timer
    Timer.periodic(Duration(minutes: repeatMinutes), (timer) async {
      final pending =
          await flutterLocalNotificationsPlugin.pendingNotificationRequests();
      final stillExists = pending.any((n) => n.id == notificationId);
      if (!stillExists) {
        timer.cancel(); // tarefa foi concluída
      } else {
        await flutterLocalNotificationsPlugin.show(
          notificationId,
          'Tarefa: $title',
          description,
          details,
          payload: 'concluir|$taskId',
        );
      }
    });
  }

  static Future<void> showInstantNotification(String title, String body) async {
    const android = AndroidNotificationDetails(
      'firebase_notification',
      'Firebase Notifications',
      channelDescription: 'Notificações instantâneas do Firebase',
      importance: Importance.max,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
      enableVibration: true,
      playSound: true,
    );

    const details = NotificationDetails(android: android);
    await flutterLocalNotificationsPlugin.show(0, title, body, details);
  }

  static Future<void> cancelNotification(int id) async {
    await flutterLocalNotificationsPlugin.cancel(id);
    print("Notificação $id cancelada");
  }
}
