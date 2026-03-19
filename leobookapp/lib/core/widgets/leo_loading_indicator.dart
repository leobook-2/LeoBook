// leo_loading_indicator.dart: Branded loading/progress widget for LeoBook.
// Part of LeoBook App — Core Widgets

import 'package:flutter/material.dart';
import 'package:leobookapp/core/constants/app_colors.dart';

/// A professional, branded loading indicator with optional label.
///
/// Usage:
/// ```dart
/// const LeoLoadingIndicator()               // default spinner
/// const LeoLoadingIndicator(size: 24)       // small spinner (inline)
/// const LeoLoadingIndicator(label: 'Loading matches...')
/// ```
class LeoLoadingIndicator extends StatefulWidget {
  final double size;
  final String? label;
  final Color? color;

  const LeoLoadingIndicator({
    super.key,
    this.size = 36,
    this.label,
    this.color,
  });

  @override
  State<LeoLoadingIndicator> createState() => _LeoLoadingIndicatorState();
}

class _LeoLoadingIndicatorState extends State<LeoLoadingIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final color = widget.color ?? AppColors.primary;

    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: widget.size,
            height: widget.size,
            child: AnimatedBuilder(
              animation: _controller,
              builder: (context, child) {
                return CustomPaint(
                  painter: _ArcPainter(
                    progress: _controller.value,
                    color: color,
                    strokeWidth: widget.size < 28 ? 2.0 : 3.0,
                  ),
                );
              },
            ),
          ),
          if (widget.label != null) ...[
            SizedBox(height: widget.size < 28 ? 6 : 12),
            Text(
              widget.label!,
              style: TextStyle(
                color: AppColors.textGrey,
                fontSize: widget.size < 28 ? 10 : 12,
                fontWeight: FontWeight.w500,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _ArcPainter extends CustomPainter {
  final double progress;
  final Color color;
  final double strokeWidth;

  _ArcPainter({
    required this.progress,
    required this.color,
    required this.strokeWidth,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Rect.fromLTWH(0, 0, size.width, size.height);

    // Background track
    final bgPaint = Paint()
      ..color = color.withValues(alpha: 0.12)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;
    canvas.drawArc(rect, 0, 3.14159 * 2, false, bgPaint);

    // Animated arc
    final fgPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    final startAngle = progress * 3.14159 * 2;
    const sweepAngle = 3.14159 * 1.2; // 216 degrees
    canvas.drawArc(rect, startAngle, sweepAngle, false, fgPaint);
  }

  @override
  bool shouldRepaint(_ArcPainter old) => old.progress != progress;
}
