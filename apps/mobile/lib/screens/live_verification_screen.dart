import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:image_picker/image_picker.dart';

import '../services/api_service.dart';

class LiveVerificationScreen extends StatefulWidget {
  const LiveVerificationScreen({super.key});

  @override
  State<LiveVerificationScreen> createState() => _LiveVerificationScreenState();
}

class _LiveVerificationScreenState extends State<LiveVerificationScreen> {
  CameraController? _cameraController;
  final ImagePicker _imagePicker = ImagePicker();
  bool _loading = true;
  bool _cameraReady = false;
  bool _processing = false;
  String? _cameraError;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) throw StateError('No camera was found');
      final camera = cameras.firstWhere(
        (item) => item.lensDirection == CameraLensDirection.back,
        orElse: () => cameras.first,
      );
      final controller = CameraController(camera, ResolutionPreset.high, enableAudio: false);
      await controller.initialize();
      if (!mounted) {
        await controller.dispose();
        return;
      }
      _cameraController = controller;
      setState(() {
        _cameraReady = true;
        _loading = false;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _cameraError = error.toString();
        _loading = false;
      });
    }
  }

  Future<void> _capture() async {
    if (_processing) return;
    if (!_cameraReady || _cameraController == null) {
      await _pickImage();
      return;
    }
    setState(() => _processing = true);
    try {
      final photo = await _cameraController!.takePicture();
      await _scan(photo.path);
    } catch (error) {
      _showError('Could not capture image: $error');
    } finally {
      if (mounted) setState(() => _processing = false);
    }
  }

  Future<void> _pickImage() async {
    if (_processing) return;
    setState(() => _processing = true);
    try {
      final photo = await _imagePicker.pickImage(source: ImageSource.gallery, imageQuality: 92);
      if (photo != null) await _scan(photo.path);
    } catch (error) {
      _showError('Could not select image: $error');
    } finally {
      if (mounted) setState(() => _processing = false);
    }
  }

  Future<void> _scan(String path) async {
    final result = await ApiService.scanVerify(imagePath: path, productName: 'Package label');
    if (!mounted) return;
    if (result.labelDetected) {
      Navigator.pushReplacementNamed(context, '/scan-evaluation');
    } else {
      _showRetryDialog();
    }
  }

  void _showRetryDialog() {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      builder: (sheetContext) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.warning_amber_rounded, color: Colors.red, size: 40),
              const SizedBox(height: 10),
              Text('No label detected', style: GoogleFonts.inter(fontSize: 20, fontWeight: FontWeight.w700)),
              const SizedBox(height: 6),
              const Text('Keep the complete package inside the frame and try again.'),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pop(sheetContext);
                    _capture();
                  },
                  child: const Text('Try again'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showError(String message) {
    if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan package'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => Navigator.pop(context)),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: _loading
                  ? const Center(child: CircularProgressIndicator())
                  : _cameraReady && _cameraController != null
                      ? Stack(
                          fit: StackFit.expand,
                          children: [
                            CameraPreview(_cameraController!),
                            IgnorePointer(
                              child: Center(
                                child: FractionallySizedBox(
                                  widthFactor: 0.86,
                                  heightFactor: 0.58,
                                  child: DecoratedBox(
                                    decoration: BoxDecoration(border: Border.all(color: Colors.white, width: 2), borderRadius: BorderRadius.circular(18)),
                                  ),
                                ),
                              ),
                            ),
                            Positioned(
                              top: 16,
                              left: 16,
                              right: 16,
                              child: Center(
                                child: DecoratedBox(
                                  decoration: const BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.all(Radius.circular(20))),
                                  child: const Padding(
                                    padding: EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                                    child: Text('Fit label inside the frame', style: TextStyle(color: Colors.white)),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        )
                      : Center(
                          child: Padding(
                            padding: const EdgeInsets.all(24),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.no_photography_outlined, size: 56),
                                const SizedBox(height: 12),
                                const Text('Camera unavailable', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
                                if (_cameraError != null) ...[
                                  const SizedBox(height: 8),
                                  Text(_cameraError!, textAlign: TextAlign.center),
                                ],
                                const SizedBox(height: 16),
                                OutlinedButton.icon(onPressed: _pickImage, icon: const Icon(Icons.photo_library_outlined), label: const Text('Choose from gallery')),
                              ],
                            ),
                          ),
                        ),
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(child: OutlinedButton.icon(onPressed: _processing ? null : _pickImage, icon: const Icon(Icons.photo_library_outlined), label: const Text('Gallery'))),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: ElevatedButton.icon(
                      onPressed: _processing ? null : _capture,
                      icon: _processing ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.camera_alt_outlined),
                      label: Text(_processing ? 'Scanning...' : 'Capture and scan'),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
