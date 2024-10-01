import 'dart:io' as io;
import 'dart:convert'; // Required for Encoding, utf8
import 'package:logger/logger.dart';
import 'package:path/path.dart' as path;

class LoggerService {
  static final LoggerService _instance = LoggerService._internal();
  late Logger logger;
  io.File? logFile;

  factory LoggerService() {
    return _instance;
  }

  LoggerService._internal() {
    _initLogger();
  }

  void _initLogger() {
    if (!_isWeb()) {
      final String logFilePath = _getLogFilePath();
      logFile = io.File(logFilePath);
    }

    logger = Logger(
      printer: PrettyPrinter(),
      output: _isWeb() ? null : FileOutput(file: logFile!),
    );
  }

  String _getLogFilePath() {
    final String projectRoot =
        _isWeb() ? '' : path.dirname(io.Platform.resolvedExecutable);
    final logsDir = io.Directory(path.join(projectRoot, 'logs'));
    if (!logsDir.existsSync()) {
      logsDir.createSync();
    }
    return path.join(logsDir.path, 'flutter_app.log');
  }

  bool _isWeb() {
    try {
      return identical(0, 0.0);
    } catch (e) {
      return true;
    }
  }

  void info(String message) {
    logger.i(message);
  }

  void debug(String message) {
    logger.d(message);
  }

  void error(String message, [dynamic error, StackTrace? stackTrace]) {
    final errorMessage = '$message Error: $error, StackTrace: $stackTrace';
    logger.e(errorMessage);
  }

  void warning(String message) {
    logger.w(message);
  }

  Future<String> getLogFilePath() async {
    return logFile?.path ?? '';
  }

  Future<String> getLogs() async {
    return logFile?.readAsString() ?? '';
  }

  Future<void> clearLogs() async {
    await logFile?.writeAsString('');
  }
}

class FileOutput extends LogOutput {
  final io.File file;
  final bool overrideExisting;
  final Encoding encoding;

  FileOutput({
    required this.file,
    this.overrideExisting = false,
    this.encoding = utf8,
  });

  @override
  void output(OutputEvent event) {
    final output = event.lines.join('\n');
    file.writeAsStringSync('$output\n',
        mode: io.FileMode.append, encoding: encoding);
  }
}
