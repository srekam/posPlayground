import 'package:flutter/material.dart';
import 'tokens.dart';

class AppTheme {
  static ThemeData dark({String colorScheme = 'default'}) {
    ColorScheme colorSchemeData;

    switch (colorScheme) {
      case 'lollipop':
        colorSchemeData = const ColorScheme.dark(
          primary: Color(0xFFE91E63),
          secondary: Color(0xFF9C27B0),
          tertiary: Color(0xFF00BCD4),
          surface: Color(0xFF1A1A1A),
          error: Color(0xFFF44336),
          onPrimary: Colors.white,
          onSecondary: Colors.white,
          onTertiary: Colors.white,
          onSurface: Colors.white,
          onError: Colors.white,
        );
        break;
      case 'monochrome':
        colorSchemeData = const ColorScheme.dark(
          primary: Colors.white,
          secondary: Colors.grey,
          tertiary: Colors.white70,
          surface: Color(0xFF1A1A1A),
          error: Color(0xFF666666),
          onPrimary: Colors.black,
          onSecondary: Colors.black,
          onTertiary: Colors.black,
          onSurface: Colors.white,
          onError: Colors.white,
        );
        break;
      default:
        colorSchemeData = ColorScheme.fromSeed(
          seedColor: AppColors.primarySeed,
          brightness: Brightness.dark,
        );
    }

    final base = ThemeData(
      colorScheme: colorSchemeData,
      useMaterial3: true,
      brightness: Brightness.dark,
    );

    return base.copyWith(
      scaffoldBackgroundColor: colorSchemeData.surface,
      textTheme: base.textTheme.apply(
        bodyColor: colorSchemeData.onSurface,
        displayColor: colorSchemeData.onSurface,
      ),
      cardTheme: const CardThemeData(elevation: 0),
    );
  }

  static ThemeData light({String colorScheme = 'default'}) {
    ColorScheme colorSchemeData;

    switch (colorScheme) {
      case 'lollipop':
        colorSchemeData = const ColorScheme.light(
          primary: Color(0xFFE91E63),
          secondary: Color(0xFF9C27B0),
          tertiary: Color(0xFF00BCD4),
          surface: Color(0xFFFFFBFE),
          error: Color(0xFFF44336),
          onPrimary: Colors.white,
          onSecondary: Colors.white,
          onTertiary: Colors.white,
          onSurface: Colors.black,
          onError: Colors.white,
        );
        break;
      case 'monochrome':
        colorSchemeData = const ColorScheme.light(
          primary: Colors.black,
          secondary: Colors.grey,
          tertiary: Colors.black87,
          surface: Color(0xFFFFFFFF),
          error: Color(0xFF666666),
          onPrimary: Colors.white,
          onSecondary: Colors.white,
          onTertiary: Colors.white,
          onSurface: Colors.black,
          onError: Colors.white,
        );
        break;
      default:
        colorSchemeData = ColorScheme.fromSeed(
          seedColor: AppColors.primarySeed,
          brightness: Brightness.light,
        );
    }

    final base = ThemeData(
      colorScheme: colorSchemeData,
      useMaterial3: true,
      brightness: Brightness.light,
    );

    return base.copyWith(
      scaffoldBackgroundColor: colorSchemeData.surface,
      textTheme: base.textTheme.apply(
        bodyColor: colorSchemeData.onSurface,
        displayColor: colorSchemeData.onSurface,
      ),
      cardTheme: const CardThemeData(elevation: 0),
    );
  }
}
