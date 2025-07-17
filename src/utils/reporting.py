import pandas as pd
import plotly.graph_objects as go
from jinja2 import Template
import smtplib
import telegram
from datetime import datetime

class Report:
    def __init__(self, stock_data, predictions, transactions, metrics):
        self.stock_data = stock_data
        self.predictions = predictions
        self.transactions = transactions
        self.metrics = metrics
        
    def generate_html(self):
        """Generate HTML report with interactive charts"""
        template = Template('''
            <html>
                <head>
                    <title>Trading Strategy Report</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container">
                        <h1>Trading Strategy Report</h1>
                        <h2>Performance Metrics</h2>
                        {{ metrics_table }}
                        
                        <h2>Charts</h2>
                        {{ charts }}
                        
                        <h2>Recent Transactions</h2>
                        {{ transactions_table }}
                    </div>
                </body>
            </html>
        ''')
        
        return template.render(
            metrics_table=self.metrics.to_html(),
            charts=self.generate_plotly_charts(),
            transactions_table=pd.DataFrame(self.transactions).to_html()
        )
    
    def send_email(self, recipient, smtp_settings):
        """Email the report"""
        msg = self.generate_html()
        # Add email sending logic
        
    def send_telegram(self, bot_token, chat_id):
        """Send summary to Telegram"""
        bot = telegram.Bot(token=bot_token)
        msg = f"Trading Update\n\nSharpe: {self.metrics['sharpe']:.2f}\nReturns: {self.metrics['returns']:.2%}"
        bot.send_message(chat_id=chat_id, text=msg)