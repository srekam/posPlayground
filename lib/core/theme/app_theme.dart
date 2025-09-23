import 'package:flutter/material.dart';
import 'tokens.dart';

class AppTheme {
  static ThemeData dark() {
    final base = ThemeData(
      colorSchemeSeed: AppColors.primarySeed,
      useMaterial3: true,
      brightness: Brightness.dark,
    );
    return base.copyWith(
      scaffoldBackgroundColor: AppColors.surfaceDark,
      textTheme: base.textTheme.apply(
        bodyColor: AppColors.onSurfaceDark,
        displayColor: AppColors.onSurfaceDark,
      ),
      cardTheme: const CardThemeData(elevation: 0),
    );
  }
}


