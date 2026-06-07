import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../app/branding/portal_backdrop.dart';
import '../../app/theme/app_spacing.dart';
import 'legal_content.dart';

/// Экран юридического документа (Политика / Условия). Доступен без авторизации
/// (см. router redirect): модератор и пользователь открывают его прямо с экрана
/// регистрации. Контент — из [legal_content], без сетевых запросов.
class LegalScreen extends StatelessWidget {
  const LegalScreen({super.key, required this.document});

  final LegalDocument document;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      body: PortalBackdrop(
        child: SafeArea(
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.sm,
                  vertical: AppSpacing.xs,
                ),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back),
                      tooltip: 'Назад',
                      onPressed: () {
                        if (context.canPop()) {
                          context.pop();
                        } else {
                          context.go('/register');
                        }
                      },
                    ),
                    Expanded(
                      child: Text(
                        document.title,
                        style: theme.textTheme.titleMedium,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Center(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.xl,
                      vertical: AppSpacing.lg,
                    ),
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 640),
                      child: GlassCard(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: _buildContent(theme),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  List<Widget> _buildContent(ThemeData theme) {
    final widgets = <Widget>[
      Text(document.title, style: theme.textTheme.headlineSmall),
      const SizedBox(height: AppSpacing.xs),
      Text(
        document.subtitle,
        style: theme.textTheme.bodySmall?.copyWith(
          color: theme.colorScheme.onSurfaceVariant,
        ),
      ),
      const SizedBox(height: AppSpacing.lg),
    ];

    for (final section in document.sections) {
      if (section.heading != null) {
        widgets.add(Padding(
          padding: const EdgeInsets.only(top: AppSpacing.md),
          child: Text(section.heading!, style: theme.textTheme.titleSmall),
        ));
        widgets.add(const SizedBox(height: AppSpacing.xs));
      }
      for (final paragraph in section.paragraphs) {
        widgets.add(Padding(
          padding: const EdgeInsets.only(bottom: AppSpacing.sm),
          child: Text(
            paragraph,
            style: theme.textTheme.bodyMedium?.copyWith(height: 1.45),
          ),
        ));
      }
    }
    return widgets;
  }
}
