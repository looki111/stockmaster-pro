# StockMaster Pro - Smart Inventory System

## Overview

The Smart Inventory System is an enhanced inventory management solution for StockMaster Pro that provides detailed tracking of raw materials, consumption rules, and inventory movements. It enables coffee shops to efficiently manage their stock, reduce waste, and make data-driven decisions.

## Key Features

- **Enhanced Raw Material Tracking**: Track detailed information about raw materials including cost, expiry dates, storage locations, and more.
- **Consumption Rules**: Define how products consume raw materials with support for variants and waste factors.
- **Inventory Transactions**: Record all inventory movements with detailed transaction history.
- **Stock Counts**: Perform periodic inventory counts and reconcile discrepancies.
- **Inventory Adjustments**: Make manual adjustments to inventory with approval workflows.
- **Daily Stock Reports**: Generate daily reports on inventory status, consumption, and waste.
- **Low Stock Alerts**: Receive notifications when items are running low.
- **Expiry Tracking**: Monitor expiry dates and get alerts for items expiring soon.

## Models

### Raw Material

Enhanced raw material model with detailed tracking:

- Basic information: name, unit, quantity, alert threshold
- Cost tracking: cost_price, average_cost, last_purchase_price
- Dates: last_purchase_date, expiry_date, manufacturing_date
- Storage: storage_location, barcode, sku
- Consumption metrics: daily_usage_rate, reorder_point, reorder_quantity, waste_percentage
- Status: is_active, status (in_stock, low_stock, out_of_stock, discontinued)
- Additional info: description, notes, image, category

### Consumption Rule

Defines how raw materials are consumed by products:

- product_id: Product that consumes the raw material
- raw_material_id: Raw material being consumed
- quantity: Amount of raw material used
- unit: Unit of measurement
- waste_factor: Percentage of additional material to account for waste
- condition_type/value: Optional conditions (e.g., only for large size)

### Inventory Transaction

Records all inventory movements:

- transaction_type: purchase, sale, adjustment, transfer, waste
- reference_type/id: Related entity (order, purchase, adjustment)
- raw_material_id/product_id: Item being transacted
- quantity: Amount (positive for additions, negative for deductions)
- unit_cost: Cost per unit at time of transaction

### Stock Count

Periodic inventory counts:

- count_date: Date of the count
- status: draft, in_progress, completed, cancelled
- items: Individual items counted (StockCountItem)

### Inventory Adjustment

Manual adjustments to inventory:

- adjustment_type: addition, deduction, waste, spoilage, correction
- status: pending, approved, rejected
- reason: Reason for adjustment
- items: Individual items adjusted (InventoryAdjustmentItem)

### Daily Stock Report

Daily inventory status reports:

- report_date: Date of the report
- summary metrics: total_items, low_stock_items, out_of_stock_items, total_value, total_consumption, waste_percentage
- items: Individual item reports (DailyStockReportItem)

## Workflow

### Order Processing

When an order is created:

1. Order is saved to the database
2. `order.process_inventory(user_id)` is called
3. The system looks up consumption rules for each product in the order
4. Raw materials are deducted based on consumption rules
5. Inventory transactions are created to record the consumption
6. Low stock alerts are generated if necessary

### Inventory Management

1. **Adding Raw Materials**: Add new raw materials with detailed information
2. **Defining Consumption Rules**: Define how products consume raw materials
3. **Stock Counts**: Perform periodic inventory counts to reconcile discrepancies
4. **Inventory Adjustments**: Make manual adjustments to inventory with approval workflows
5. **Daily Reports**: Generate daily reports on inventory status, consumption, and waste

## API Endpoints

### Raw Materials

- `GET /inventory/raw-materials`: List raw materials with optional filtering
- `POST /inventory/raw-materials/add`: Add a new raw material
- `GET /inventory/raw-materials/<id>/edit`: Edit a raw material
- `POST /inventory/raw-materials/<id>/adjust`: Adjust raw material quantity

### Consumption Rules

- `GET /inventory/consumption-rules`: List consumption rules with optional filtering
- `POST /inventory/consumption-rules/add`: Add a new consumption rule
- `GET /inventory/consumption-rules/<id>/edit`: Edit a consumption rule
- `POST /inventory/consumption-rules/<id>/delete`: Delete a consumption rule

### Stock Reports

- `GET /inventory/reports`: List stock reports
- `POST /inventory/reports/generate`: Generate a new stock report
- `GET /inventory/reports/<id>`: View a stock report
- `GET /inventory/reports/<id>/export`: Export a stock report as CSV

## Database Migration

To upgrade your existing database to support the new inventory system:

1. Run the migration script:
   ```
   python -m backend.migrations.inventory_upgrade
   ```

2. The script will:
   - Update existing tables (raw_materials, products, recipes, orders, order_items)
   - Create new tables for the inventory system
   - Migrate existing data to the new schema

## Best Practices

1. **Regular Stock Counts**: Perform regular stock counts to ensure accuracy
2. **Waste Tracking**: Track waste to identify areas for improvement
3. **Expiry Management**: Monitor expiry dates and use FIFO (First In, First Out) method
4. **Reorder Points**: Set appropriate reorder points to avoid stockouts
5. **Data Analysis**: Use daily reports to analyze consumption patterns and optimize inventory

## Troubleshooting

### Common Issues

1. **Inventory Discrepancies**: If inventory counts don't match system values:
   - Check for unrecorded waste or consumption
   - Verify that all orders are properly processing inventory
   - Perform a full inventory count and reconciliation

2. **Missing Consumption Rules**: If raw materials aren't being deducted:
   - Verify that consumption rules are defined for all products
   - Check that the rules have the correct quantities and units

3. **Database Migration Errors**:
   - Backup your database before migration
   - Check the migration logs for specific errors
   - Contact support if you encounter persistent issues

## Future Enhancements

1. **Predictive Inventory**: AI-based prediction of inventory needs
2. **Supplier Integration**: Direct ordering from suppliers when stock is low
3. **Batch Tracking**: Track inventory by batch/lot number
4. **Mobile Scanning**: Barcode/QR code scanning for inventory management
5. **Advanced Analytics**: Enhanced reporting and analytics
