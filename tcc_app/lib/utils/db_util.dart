import 'package:sqflite/sqflite.dart' as sql;
import 'package:path/path.dart' as path;

class DbUtil {
  static Future<sql.Database> database() async {
    final dbPath = await sql.getDatabasesPath();
    return sql.openDatabase(
      path.join(dbPath, 'appbanco.db'),
      onCreate: (db, version) {
        db
            .execute(
              'CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT, description TEXT, time TEXT, complete INTEGER)',
            )
            .then((_) {
              return db.execute(
                'CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT)',
              );
            });
      },
      version: 1,
    );
  }

  static Future<void> insertData(String table, Map<String, Object> data) async {
    final db = await database();
    await db.insert(
      table,
      data,
      conflictAlgorithm: sql.ConflictAlgorithm.replace,
    );
  }

  static Future<void> updateData(String table, Map<String, Object> data) async {
    final db = await database();
    await db.update(table, data, where: 'id = ?', whereArgs: [data['id']]);
  }

  static Future<void> deleteData(String table, String id) async {
    final db = await database();
    await db.delete(table, where: 'id = ?', whereArgs: [id]);
  }

  static Future<List<Map<String, dynamic>>> getData(String table) async {
    final db = await database();
    return db.query(table);
  }

  static Future<void> updateComplete(String taskId, bool complete) async {
    final db = await database();
    await db.update(
      'tasks',
      {
        'complete': complete ? 1 : 0,
      }, // Converte bool para 1 (true) ou 0 (false)
      where: 'id = ?',
      whereArgs: [taskId],
    );
  }

  static Future<void> insertSetting(String key, String value) async {
    final db = await database();
    await db.insert('settings', {
      'key': key,
      'value': value,
    }, conflictAlgorithm: sql.ConflictAlgorithm.replace);
  }

  static Future<String?> getSetting(String key) async {
    final db = await database();
    final List<Map<String, dynamic>> maps = await db.query(
      'settings',
      where: 'key = ?',
      whereArgs: [key],
    );
    if (maps.isNotEmpty) {
      return maps.first['value'] as String?;
    }
    return null;
  }
}
