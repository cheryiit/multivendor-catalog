import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../services/logger_service.dart';

class ProductListScreen extends StatefulWidget {
  final int? vendorId;

  const ProductListScreen({super.key, this.vendorId});

  @override
  ProductListScreenState createState() => ProductListScreenState();
}

class ProductListScreenState extends State<ProductListScreen> {
  List products = [];
  bool isLoading = true;
  String message = '';
  final LoggerService logger = LoggerService();

  @override
  void initState() {
    super.initState();
    logger.info('ProductListScreen initialized');
    fetchProducts();
  }

  Future<void> fetchProducts() async {
    String url = 'http://10.0.2.2:8000/products';
    if (widget.vendorId != null) {
      url += '?vendor_id=${widget.vendorId}';
    }
    logger.debug('Fetching products from URL: $url');

    try {
      final response = await http.get(Uri.parse(url));
      logger
          .debug('Received response with status code: ${response.statusCode}');

      if (response.statusCode == 200) {
        setState(() {
          products = json.decode(response.body)['products'];
          isLoading = false;
        });
        logger.info('Successfully loaded ${products.length} products');
      } else if (response.statusCode == 202) {
        logger.info('Data is being fetched, waiting to retry');
        setState(() {
          message = 'Data is being fetched, please wait...';
        });
        Future.delayed(const Duration(seconds: 5), fetchProducts);
      } else {
        logger.error(
            'Failed to load products. Status code: ${response.statusCode}');
        setState(() {
          message = 'Failed to load products';
          isLoading = false;
        });
      }
    } catch (e, stackTrace) {
      logger.error('Error fetching products', e, stackTrace);
      setState(() {
        message = 'Error: ${e.toString()}';
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    logger.debug('Building ProductListScreen. isLoading: $isLoading');
    if (isLoading) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Product List'),
        ),
        body: Center(
          child: message.isEmpty
              ? const CircularProgressIndicator()
              : Text(message),
        ),
      );
    } else {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Product List'),
        ),
        body: ListView.builder(
          itemCount: products.length,
          itemBuilder: (context, index) {
            final product = products[index];
            logger.debug('Building list item for product: ${product['name']}');
            return ListTile(
              leading: const Image(
                image: AssetImage('assets/images/image.png'),
              ),
              title: Text(product['name']),
              subtitle: Text('\$${product['price']}'),
            );
          },
        ),
      );
    }
  }
}
