import 'package:flutter/material.dart';

const Color corP = Color.fromRGBO(13, 71, 161, 1);

ThemeData lightMode = ThemeData(
  brightness: Brightness.light,
  colorScheme: ColorScheme.fromSeed(
    seedColor: corP,
    primary: corP,
    secondary: const Color.fromARGB(255, 115, 192, 255),
    tertiary: Colors.white,
  ),
  useMaterial3: true,
  appBarTheme: const AppBarTheme(
    centerTitle: true,
    backgroundColor: Color.fromRGBO(13, 71, 161, 1),
    titleTextStyle: TextStyle(
      color: Colors.white,
      fontSize: 22,
      fontWeight: FontWeight.bold,
    ),
    iconTheme: IconThemeData(color: Colors.white),
  ),
  buttonTheme: const ButtonThemeData(
    buttonColor: corP,
    textTheme: ButtonTextTheme.primary,
  ),
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: corP,
      foregroundColor: Colors.white,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
    ),
  ),
  floatingActionButtonTheme: const FloatingActionButtonThemeData(
    backgroundColor: corP,
  ),
  textTheme: const TextTheme(
    bodyLarge: TextStyle(color: Colors.black87, fontSize: 14),
    bodyMedium: TextStyle(color: Colors.black54, fontSize: 14),
    displayLarge: TextStyle(
      color: corP,
      fontSize: 32,
      fontWeight: FontWeight.bold,
    ),
    titleLarge: TextStyle(
      color: corP,
      fontSize: 20,
      fontWeight: FontWeight.bold,
    ),
  ),
);

ThemeData darkMode = ThemeData(
  brightness: Brightness.dark,
  colorScheme: const ColorScheme.dark(
    primary: Color.fromRGBO(76, 19, 248, 1),
    secondary: Color.fromARGB(255, 133, 255, 137),
    tertiary: Color.fromARGB(255, 151, 152, 161),
  ),

  useMaterial3: true,
  appBarTheme: const AppBarTheme(
    centerTitle: true,
    backgroundColor: Color.fromRGBO(69, 39, 160, 1),
    titleTextStyle: TextStyle(
      color: Colors.white,
      fontSize: 22,
      fontWeight: FontWeight.bold,
    ),
    iconTheme: IconThemeData(color: Colors.white),
  ),
  // Additional Theme Customizations
  buttonTheme: const ButtonThemeData(
    buttonColor: Colors.deepPurple,
    textTheme: ButtonTextTheme.primary,
  ),
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: Colors.deepPurple[700],
      foregroundColor: Colors.white,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
    ),
  ),
  floatingActionButtonTheme: FloatingActionButtonThemeData(
    backgroundColor: Colors.deepPurple[700],
  ),
  textTheme: const TextTheme(
    bodyLarge: TextStyle(color: Colors.white70, fontSize: 14),
    bodyMedium: TextStyle(color: Colors.white54, fontSize: 14),
    displayLarge: TextStyle(
      color: Colors.deepPurpleAccent,
      fontSize: 32,
      fontWeight: FontWeight.bold,
    ),
    titleLarge: TextStyle(
      color: Colors.deepPurpleAccent,
      fontSize: 20,
      fontWeight: FontWeight.bold,
    ),
  ),
);
