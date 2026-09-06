import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../widgets/progress_ring.dart';

class ScanEvaluationScreen extends StatelessWidget {
  const ScanEvaluationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final findings = const [
      ('MRP font size below minimum', '2.1mm detected, 4.0mm required', 'HIGH', Color(0xFFE53935), Color(0xFFFFEBEE), 'Rule LM-PC-2011-6(1)'),
      ('Missing country of origin', 'Declaration absent on side panels', 'MEDIUM', Color(0xFFFB8C00), Color(0xFFFFF3E0), 'Rule LM-PC-2011-6(1)(j)'),
      ('Net quantity unit non-standard', "Declared as 'gms' instead of standard 'g'", 'LOW', Color(0xFF2E7D32), Color(0xFFE8F5E9), 'Rule LM-PC-2011-6(1)(e)'),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan evaluation'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context)),
      ),
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
              sliver: SliverToBoxAdapter(
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18)),
                  child: Row(
                    children: [
                      Container(
                        width: 68,
                        height: 68,
                        decoration: BoxDecoration(color: const Color(0xFFE8F5E9), borderRadius: BorderRadius.circular(14)),
                        child: const Icon(Icons.inventory_2_outlined, color: Color(0xFF005F52), size: 32),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Package label', maxLines: 2, overflow: TextOverflow.ellipsis, style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w700)),
                            const SizedBox(height: 4),
                            Text('OCR and compliance analysis', maxLines: 1, overflow: TextOverflow.ellipsis, style: GoogleFonts.inter(fontSize: 12, color: const Color(0xFF6B7280))),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      const ProgressRing(progress: 0.62, size: 58, color: Color(0xFFE53935)),
                    ],
                  ),
                ),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              sliver: SliverToBoxAdapter(
                child: Row(
                  children: [
                    Expanded(child: Text('Non-compliances (3)', maxLines: 1, overflow: TextOverflow.ellipsis, style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w700))),
                    Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5), decoration: BoxDecoration(color: const Color(0xFFFFEBEE), borderRadius: BorderRadius.circular(8)), child: const Text('Action required', style: TextStyle(color: Color(0xFFE53935), fontSize: 10, fontWeight: FontWeight.w700))),
                  ],
                ),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              sliver: SliverList(
                delegate: SliverChildBuilderDelegate(
                  (context, index) {
                    final item = findings[index];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Expanded(child: Text(item.$1, maxLines: 2, overflow: TextOverflow.ellipsis, style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w700))),
                                const SizedBox(width: 8),
                                Container(padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3), decoration: BoxDecoration(color: item.$5, borderRadius: BorderRadius.circular(99)), child: Text(item.$3, style: TextStyle(color: item.$4, fontSize: 9, fontWeight: FontWeight.w800))),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(item.$2, maxLines: 2, overflow: TextOverflow.ellipsis, style: GoogleFonts.inter(fontSize: 12, color: const Color(0xFF6B7280))),
                            const SizedBox(height: 8),
                            Row(children: [const Icon(Icons.book_outlined, size: 14, color: Color(0xFF005F52)), const SizedBox(width: 6), Expanded(child: Text(item.$6, maxLines: 1, overflow: TextOverflow.ellipsis, style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w600)))]),
                          ],
                        ),
                      ),
                    );
                  },
                  childCount: findings.length,
                ),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
              sliver: SliverToBoxAdapter(
                child: ElevatedButton.icon(
                  onPressed: () => Navigator.pushNamed(context, '/report'),
                  icon: const Icon(Icons.picture_as_pdf_outlined),
                  label: const Text('Open verification report'),
                  style: ElevatedButton.styleFrom(minimumSize: const Size.fromHeight(50)),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
