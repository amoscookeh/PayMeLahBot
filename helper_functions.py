def format_line_items(data):
    line_items = data['result']['lineItems']
    output_data = []
    for item in line_items:
        line_item = {
            'qty': item['qty'],
            'descClean': item['descClean'],
            'lineTotal': item['lineTotal']
        }
        output_data.append(line_item)
    return output_data