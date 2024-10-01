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
  int retryCount = 0;
  static const int maxRetries = 3;

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
      logger.debug('Response body: ${response.body}');

      if (response.statusCode == 200) {
        final decodedBody = json.decode(response.body);
        setState(() {
          products = decodedBody['products'];
          isLoading = false;
          message = '';
        });
        logger.info('Successfully loaded ${products.length} products');
      } else if (response.statusCode == 202) {
        logger.info('Data is being fetched, waiting to retry');
        setState(() {
          message = 'Data is being fetched, please wait...';
        });
        if (retryCount < maxRetries) {
          retryCount++;
          logger.debug('Retry attempt $retryCount of $maxRetries');
          Future.delayed(const Duration(seconds: 5), fetchProducts);
        } else {
          setState(() {
            isLoading = false;
            message = 'Failed to load products after $maxRetries attempts';
          });
          logger.error('Max retry attempts reached');
        }
      } else {
        logger.error(
            'Failed to load products. Status code: ${response.statusCode}');
        setState(() {
          message =
              'Failed to load products. Status code: ${response.statusCode}';
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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Product List'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {
                isLoading = true;
                message = '';
                retryCount = 0;
              });
              fetchProducts();
            },
          ),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : message.isNotEmpty
              ? Center(child: Text(message))
              : products.isEmpty
                  ? const Center(child: Text('No products found'))
                  : ListView.builder(
                      itemCount: products.length,
                      itemBuilder: (context, index) {
                        final product = products[index];
                        logger.debug(
                            'Building list item for product: ${product['name']}');
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
