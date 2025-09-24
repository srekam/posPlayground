import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

class SettingsState {
  final ThemeMode themeMode;
  final String colorScheme;
  final String language;
  final bool showBackgroundImage;

  const SettingsState({
    this.themeMode = ThemeMode.dark,
    this.colorScheme = 'default',
    this.language = 'en',
    this.showBackgroundImage = true,
  });

  SettingsState copyWith({
    ThemeMode? themeMode,
    String? colorScheme,
    String? language,
    bool? showBackgroundImage,
  }) {
    return SettingsState(
      themeMode: themeMode ?? this.themeMode,
      colorScheme: colorScheme ?? this.colorScheme,
      language: language ?? this.language,
      showBackgroundImage: showBackgroundImage ?? this.showBackgroundImage,
    );
  }
}

final settingsProvider = StateNotifierProvider<SettingsNotifier, SettingsState>((ref) {
  return SettingsNotifier();
});

class SettingsNotifier extends StateNotifier<SettingsState> {
  SettingsNotifier() : super(const SettingsState());

  void setThemeMode(ThemeMode themeMode) {
    state = state.copyWith(themeMode: themeMode);
  }

  void setColorScheme(String colorScheme) {
    state = state.copyWith(colorScheme: colorScheme);
  }

  void setLanguage(String language) {
    state = state.copyWith(language: language);
  }

  void setShowBackgroundImage(bool showBackgroundImage) {
    state = state.copyWith(showBackgroundImage: showBackgroundImage);
  }

  void resetToDefault() {
    state = const SettingsState();
  }
}
