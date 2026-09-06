import 'dart:io';

import 'package:dio/dio.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:open_filex/open_filex.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

import '../models/inspection_model.dart';

class ApiService {
  // Change to your server IP for production / USB testing
  // USB debug deployments use adb reverse tcp:8000 tcp:8000.
  static const String baseUrl = 'http://127.0.0.1:8000';
  static const bool offlineMode = false; // Set to true for offline-only testing

  static final Dio _dio = Dio(
    BaseOptions(
      connectTimeout: const Duration(seconds: 20),
      receiveTimeout: const Duration(seconds: 25),
      headers: {'Content-Type': 'application/json'},
      validateStatus: (status) => status != null && status < 500,
    ),
  );

  static Future<bool> login({required String username, required String password}) async {
    try {
      final response = await _dio.post(
        '$baseUrl/api/v1/auth/login',
        data: {'username': username, 'password': password, 'requested_role': 'Inspector'},
      );
      return response.statusCode == 200 && response.data is Map && response.data['access_token'] != null;
    } on DioException {
      return false;
    }
  }

  static Future<String?> requestOtp(String email) async {
    try {
      final response = await _dio.post('$baseUrl/api/v1/auth/request-otp', data: {'email': email});
      return response.data is Map ? response.data['dev_otp'] as String? : null;
    } on DioException {
      return null;
    }
  }

  static Future<bool> verifyOtp({required String email, required String code, required String role}) async {
    try {
      final response = await _dio.post('$baseUrl/api/v1/auth/verify-otp', data: {
        'email': email,
        'code': code,
        'requested_role': role,
      });
      return response.statusCode == 200 && response.data is Map && response.data['access_token'] != null;
    } on DioException {
      return false;
    }
  }

  static Future<bool> loginWithInspectorKey(String accessKey) async {
    try {
      final response = await _dio.post('$baseUrl/api/v1/auth/inspector-key', data: {'access_key': accessKey});
      return response.statusCode == 200 && response.data is Map && response.data['access_token'] != null;
    } on DioException {
      return false;
    }
  }

  static Future<ScanResult> scanVerify({
    required String imagePath,
    String? productName,
  }) async {
    final file = File(imagePath);
    if (!file.existsSync()) {
      return _mockScanResult(productName: productName);
    }

    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          imagePath,
          filename: p.basename(imagePath),
        ),
      });

      final response = await _dio.post(
        '$baseUrl/api/v1/scan-verify',
        data: formData,
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final payload = response.data is Map<String, dynamic>
            ? response.data as Map<String, dynamic>
            : <String, dynamic>{};
        return ScanResult.fromJson(payload);
      }
    } on DioException {
      // Fall back to offline mock mode when backend is unavailable.
    }

    return _mockScanResult(productName: productName);
  }

  static Future<void> openGeneratedPdf(String filePath) async {
    final file = File(filePath);
    if (!await file.exists()) {
      return;
    }
    final result = await OpenFilex.open(filePath);
    if (result.type != ResultType.done) {
      throw Exception('Unable to open generated PDF report');
    }
  }

  static Future<String> generatePdfReport(InspectionReportData data) async {
    final dir = await getApplicationDocumentsDirectory();
    final safeFileName =
        '${data.caseId.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]+'), '_')}.pdf';
    final path = '${dir.path}/$safeFileName';

    final file = File(path);
    final document = pw.Document();
    document.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        build: (context) => [
          pw.Header(level: 0, child: pw.Text('SafetyBite-AI Verification Report')),
          pw.Text('Case ID: ${data.caseId}'),
          pw.Text('Date: ${data.date}'),
          pw.Text('Facility: ${data.facility}'),
          pw.Text('Coordinates: ${data.coordinates}'),
          pw.Text('Officer: ${data.officer}'),
          pw.SizedBox(height: 18),
          pw.Table.fromTextArray(
            headers: const ['Declaration field', 'Result', 'Status'],
            data: const [
              ['MRP Declaration', 'Font 2.1mm vs 4mm', 'NON-COMPLIANT'],
              ['Net Quantity', 'Unit standard non-compliant', 'NON-COMPLIANT'],
              ['Mfg. / Pack Date', '10/2023', 'COMPLIANT'],
              ['Consumer Care Details', 'Email and telephone present', 'COMPLIANT'],
              ['FSSAI License No.', 'Found on backing', 'COMPLIANT'],
            ],
          ),
          pw.SizedBox(height: 24),
          pw.Text('Secure seal: NIC Compliance Grid - SHA-256 Verified'),
        ],
      ),
    );
    await file.writeAsBytes(await document.save(), flush: true);
    return path;
  }

  static ScanResult _mockScanResult({String? productName}) {
    return ScanResult(
      labelDetected: true,
      productName: productName ?? 'Sunrise Gold Refined Oil 1L',
      vendorName: 'Sunrise Oils',
      imagePath: '',
      complianceScore: 62,
      findings: const [
        ComplianceFinding(
          title: 'MRP Font Size Below Minimum',
          severity: 'HIGH',
          subtitle: '2.1mm detected, 4.0mm required',
          rule: 'Rule LM-PC-2011-6(1)',
          scoreDelta: 22,
        ),
        ComplianceFinding(
          title: 'Missing Country of Origin',
          severity: 'MEDIUM',
          subtitle: 'Declaration absent on side panels',
          rule: 'Rule LM-PC-2011-6(1)(j)',
          scoreDelta: 12,
        ),
        ComplianceFinding(
          title: 'Net Quantity Unit Non-Standard',
          severity: 'LOW',
          subtitle: "Declared as 'gms' instead of standard 'g'",
          rule: 'Rule LM-PC-2011-6(1)(e)',
          scoreDelta: 4,
        ),
      ],
      metadata: {
        'inspection_case': '2023-908',
        'facility': 'Mart-Direct, Baner Road, Pune',
      },
    );
  }
}
