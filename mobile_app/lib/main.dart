import 'package:flutter/material.dart';
import 'screens/product_list_screen.dart';
import 'services/logger_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final logger = LoggerService();
  logger.info('Application started');
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key}); // Use 'super.key' directly in the constructor

  @override
  Widget build(BuildContext context) {
    final logger = LoggerService();
    logger.debug('Building MyApp');
    return MaterialApp(
      title: 'Unified Vendor Catalog',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const MyHomePage(title: 'Unified Vendor Catalog'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage(
      {super.key,
      required this.title}); // Use 'super.key' directly in the constructor

  final String title;

  @override
  MyHomePageState createState() =>
      MyHomePageState(); // Make the state class public by removing the underscore
}

class MyHomePageState extends State<MyHomePage> {
  final logger = LoggerService();
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
    logger.debug('Counter incremented to $_counter');
  }

  @override
  Widget build(BuildContext context) {
    logger.debug('Building MyHomePage');
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'You have pushed the button this many times:',
            ),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            ElevatedButton(
              onPressed: () {
                logger.info('Navigating to ProductListScreen');
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => const ProductListScreen()),
                );
              },
              child: const Text('Go to Product List'),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    );
  }
}
