import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/branding/aperture_logo.dart';
import '../../app/branding/glow_button.dart';
import '../../app/branding/portal_backdrop.dart';
import '../../app/l10n/generated/app_localizations.dart';
import '../../app/theme/app_spacing.dart';
import '../../data/api/failure.dart';
import '../../data/api/profile_api.dart';
import 'auth_state.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  bool _obscure = true;
  bool _agreed = false;
  bool _busy = false;
  String? _formError;

  @override
  void dispose() {
    _nameCtrl.dispose();
    _emailCtrl.dispose();
    _passCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_busy) return;
    final form = _formKey.currentState;
    if (form == null || !form.validate() || !_agreed) return;
    setState(() {
      _busy = true;
      _formError = null;
    });
    try {
      await ref.read(authSessionProvider.notifier).registerAndLogin(
            email: _emailCtrl.text.trim(),
            password: _passCtrl.text,
            name: _nameCtrl.text.trim(),
          );
      // Имя живёт в UserProfile, а не в User: бэк-эндпоинт регистрации
      // принимает только email/password (см. RegisterRequest). После
      // авто-логина у нас уже есть access-токен — сохраняем имя через
      // PATCH /profile, чтобы оно сразу появилось в шапке и аватаре.
      final name = _nameCtrl.text.trim();
      if (name.isNotEmpty) {
        await ref.read(profileApiProvider).patch(name: name);
        ref.invalidate(profileProvider);
      }
      if (!mounted) return;
      context.go('/home');
    } on AppFailure catch (f) {
      if (!mounted) return;
      setState(() => _formError = f.message);
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l = AppLocalizations.of(context);
    final theme = Theme.of(context);

    return Scaffold(
      body: PortalBackdrop(child: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xxl),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: AppSpacing.xxxl),
                  const Center(child: ApertureLogo(size: 96)),
                  const SizedBox(height: AppSpacing.xl),
                  Text(
                    l.authRegisterTitle,
                    textAlign: TextAlign.center,
                    style: theme.textTheme.headlineLarge,
                  ),
                  const SizedBox(height: AppSpacing.sm),
                  Text(
                    l.authRegisterSubtitle,
                    textAlign: TextAlign.center,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: AppSpacing.xxxl),

                  Text(l.authNameLabel, style: theme.textTheme.titleSmall),
                  const SizedBox(height: AppSpacing.sm),
                  TextFormField(
                    controller: _nameCtrl,
                    decoration: InputDecoration(
                      hintText: l.authNameHint,
                      prefixIcon: const Icon(Icons.person_outline),
                    ),
                    validator: (v) =>
                        (v ?? '').trim().isEmpty ? 'Введите имя' : null,
                  ),
                  const SizedBox(height: AppSpacing.lg),

                  Text(l.authEmailLabel, style: theme.textTheme.titleSmall),
                  const SizedBox(height: AppSpacing.sm),
                  TextFormField(
                    controller: _emailCtrl,
                    decoration: InputDecoration(
                      hintText: l.authEmailHint,
                      prefixIcon: const Icon(Icons.mail_outline),
                    ),
                    keyboardType: TextInputType.emailAddress,
                    autofillHints: const [AutofillHints.email],
                    validator: (v) {
                      final t = v?.trim() ?? '';
                      if (t.isEmpty) return 'Введите email';
                      if (!t.contains('@')) return 'Некорректный email';
                      return null;
                    },
                  ),
                  const SizedBox(height: AppSpacing.lg),

                  Text(l.authPasswordLabel, style: theme.textTheme.titleSmall),
                  const SizedBox(height: AppSpacing.sm),
                  TextFormField(
                    controller: _passCtrl,
                    obscureText: _obscure,
                    decoration: InputDecoration(
                      hintText: l.authPasswordHint,
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        onPressed: () => setState(() => _obscure = !_obscure),
                        icon: Icon(
                          _obscure
                              ? Icons.visibility_off_outlined
                              : Icons.visibility_outlined,
                        ),
                      ),
                    ),
                    validator: (v) {
                      final t = v ?? '';
                      if (t.length < 8) {
                        return 'Минимум 8 символов';
                      }
                      if (!RegExp(r'\d').hasMatch(t)) {
                        return 'Пароль должен содержать цифру';
                      }
                      if (!RegExp(r'[A-Za-zА-Яа-я]').hasMatch(t)) {
                        return 'Пароль должен содержать букву';
                      }
                      return null;
                    },
                  ),

                  const SizedBox(height: AppSpacing.lg),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Checkbox(
                        value: _agreed,
                        onChanged: (v) => setState(() => _agreed = v ?? false),
                        activeColor: theme.colorScheme.primary,
                      ),
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.only(top: 12),
                          child: Text.rich(
                            TextSpan(
                              style: theme.textTheme.bodyMedium?.copyWith(
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                              children: [
                                TextSpan(text: '${l.authAgreeTermsBefore} '),
                                TextSpan(
                                  text: l.authTermsLink,
                                  style: theme.textTheme.bodyMedium?.copyWith(
                                    color: theme.colorScheme.primary,
                                    fontWeight: FontWeight.w600,
                                  ),
                                  recognizer: TapGestureRecognizer()..onTap = () {},
                                ),
                                TextSpan(text: ' ${l.authAgreeTermsAnd} '),
                                TextSpan(
                                  text: l.authPrivacyLink,
                                  style: theme.textTheme.bodyMedium?.copyWith(
                                    color: theme.colorScheme.primary,
                                    fontWeight: FontWeight.w600,
                                  ),
                                  recognizer: TapGestureRecognizer()..onTap = () {},
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),

                  if (_formError != null) ...[
                    const SizedBox(height: AppSpacing.sm),
                    _ErrorBanner(message: _formError!),
                  ],

                  const SizedBox(height: AppSpacing.xl),
                  PrimaryGlowButton(
                    onPressed: (_agreed && !_busy) ? _submit : null,
                    child: _busy
                        ? const SizedBox(
                            width: 22,
                            height: 22,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : Text(l.authRegisterCta),
                  ),

                  const SizedBox(height: AppSpacing.lg),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        l.authHasAccount,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                      TextButton(
                        onPressed: _busy ? null : () => context.go('/login'),
                        child: Text(l.authLogIn),
                      ),
                    ],
                  ),
                  const SizedBox(height: AppSpacing.xxl),
                ],
              ),
            ),
          ),
        ),
      )),
    );
  }
}

class _ErrorBanner extends StatelessWidget {
  const _ErrorBanner({required this.message});
  final String message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: theme.colorScheme.error.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(AppRadius.md),
        border: Border.all(color: theme.colorScheme.error.withValues(alpha: 0.4)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.error_outline, color: theme.colorScheme.error, size: 20),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              message,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.error,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
