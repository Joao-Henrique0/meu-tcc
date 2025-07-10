import 'dart:async';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class DbUtil {
  static Database? _db;

  static Future<Database> get database async {
    if (_db != null) return _db!;
    _db = await _initDb();
    return _db!;
  }

  static Future<Database> _initDb() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'tasks.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE tasks(
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            time TEXT,
            complete INTEGER
          )
        ''');
      },
    );
  }

  static Future<List<Map<String, dynamic>>> getData() async {
    final db = await database;
    final result = await db.query('tasks');
    return result;
  }

  static Future<String> insertData(Map<String, dynamic> data) async {
    final db = await database;
    // Gere um id se não existir (pode usar uuid ou DateTime.now().millisecondsSinceEpoch)
    String id =
        data['id']?.toString() ??
        DateTime.now().millisecondsSinceEpoch.toString();
    await db.insert('tasks', {
      'id': id,
      'title': data['title'],
      'description': data['description'],
      'time': data['time'],
      'complete': (data['complete'] == true || data['complete'] == 1) ? 1 : 0,
    }, conflictAlgorithm: ConflictAlgorithm.replace);
    return id;
  }

  static Future<void> updateData(Map<String, dynamic> data) async {
    final db = await database;
    await db.update(
      'tasks',
      {
        'title': data['title'],
        'description': data['description'],
        'time': data['time'],
        'complete': (data['complete'] == true || data['complete'] == 1) ? 1 : 0,
      },
      where: 'id = ?',
      whereArgs: [data['id']],
    );
  }

  static Future<void> deleteData(String id) async {
    final db = await database;
    await db.delete('tasks', where: 'id = ?', whereArgs: [id]);
  }

  static Future<void> updateComplete(String taskId, bool complete) async {
    final db = await database;
    await db.update(
      'tasks',
      {'complete': complete ? 1 : 0},
      where: 'id = ?',
      whereArgs: [taskId],
    );
  }
}
