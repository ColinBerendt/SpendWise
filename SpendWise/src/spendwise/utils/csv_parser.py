"""
CSV Parser - Parses bank statement CSV files into transactions

Supports multiple CSV formats:
- SpendWise standard format
- Custom formats via configuration
"""

import csv
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable


class CSVFormat(Enum):
    """Supported CSV formats"""
    SPENDWISE = "spendwise"
    # Add more bank-specific formats here
    # UBS = "ubs"
    # CREDIT_SUISSE = "credit_suisse"
    # POSTFINANCE = "postfinance"


@dataclass
class ParsedTransaction:
    """A single parsed transaction from CSV"""
    date: str  # YYYY-MM-DD format
    description: str
    amount: float
    currency: str = "CHF"
    reference: str | None = None
    
    # Optional fields
    raw_data: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "date": self.date,
            "description": self.description,
            "amount": self.amount,
            "currency": self.currency,
            "reference": self.reference,
        }


@dataclass
class ParseResult:
    """Result of parsing a CSV file"""
    success: bool
    transactions: list[ParsedTransaction]
    filename: str
    total_count: int
    error_count: int
    errors: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON/Agent consumption"""
        return {
            "success": self.success,
            "filename": self.filename,
            "total_count": self.total_count,
            "parsed_count": len(self.transactions),
            "error_count": self.error_count,
            "transactions": [t.to_dict() for t in self.transactions],
            "errors": self.errors,
        }


@dataclass
class FormatConfig:
    """Configuration for a CSV format"""
    # Column mappings (column name -> field)
    date_column: str
    description_column: str
    amount_column: str
    currency_column: str | None = None
    reference_column: str | None = None
    
    # Date parsing
    date_format: str = "%Y-%m-%d"
    
    # CSV options
    delimiter: str = ","
    skip_header: bool = True
    encoding: str = "utf-8"
    
    # Amount parsing
    decimal_separator: str = "."
    thousand_separator: str = ","
    negate_expenses: bool = False  # Some banks use positive for expenses


# Predefined format configurations
FORMAT_CONFIGS: dict[CSVFormat, FormatConfig] = {
    CSVFormat.SPENDWISE: FormatConfig(
        date_column="date",
        description_column="description",
        amount_column="amount",
        currency_column="currency",
        reference_column="reference",
        date_format="%Y-%m-%d",
    ),
}


class CSVParser:
    """
    Parses bank statement CSV files into transactions.
    
    Example usage:
        parser = CSVParser()
        result = parser.parse_file("bank_export.csv")
        
        if result.success:
            for tx in result.transactions:
                print(f"{tx.date}: {tx.description} - {tx.amount} {tx.currency}")
    """
    
    def __init__(
        self,
        format_type: CSVFormat = CSVFormat.SPENDWISE,
        config: FormatConfig | None = None,
    ):
        """
        Initialize parser with format configuration.
        
        Args:
            format_type: Predefined format to use
            config: Custom configuration (overrides format_type)
        """
        if config:
            self.config = config
        else:
            self.config = FORMAT_CONFIGS.get(format_type, FORMAT_CONFIGS[CSVFormat.SPENDWISE])
    
    def parse_file(self, filepath: str | Path) -> ParseResult:
        """
        Parse a CSV file and return transactions.
        
        Args:
            filepath: Path to the CSV file
            
        Returns:
            ParseResult with transactions and metadata
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            return ParseResult(
                success=False,
                transactions=[],
                filename=filepath.name,
                total_count=0,
                error_count=1,
                errors=[f"File not found: {filepath}"],
            )
        
        try:
            with open(filepath, "r", encoding=self.config.encoding) as f:
                return self._parse_csv(f, filepath.name)
        except Exception as e:
            return ParseResult(
                success=False,
                transactions=[],
                filename=filepath.name,
                total_count=0,
                error_count=1,
                errors=[f"Failed to read file: {str(e)}"],
            )
    
    def parse_string(self, csv_content: str, filename: str = "upload.csv") -> ParseResult:
        """
        Parse CSV content from a string.
        
        Args:
            csv_content: CSV content as string
            filename: Name to use in result
            
        Returns:
            ParseResult with transactions and metadata
        """
        import io
        return self._parse_csv(io.StringIO(csv_content), filename)
    
    def _parse_csv(self, file_obj, filename: str) -> ParseResult:
        """Internal CSV parsing logic"""
        transactions: list[ParsedTransaction] = []
        errors: list[str] = []
        row_count = 0
        
        reader = csv.DictReader(file_obj, delimiter=self.config.delimiter)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 = header)
            row_count += 1
            
            try:
                tx = self._parse_row(row, row_num)
                if tx:
                    transactions.append(tx)
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return ParseResult(
            success=len(errors) == 0,
            transactions=transactions,
            filename=filename,
            total_count=row_count,
            error_count=len(errors),
            errors=errors,
        )
    
    def _parse_row(self, row: dict, row_num: int) -> ParsedTransaction | None:
        """Parse a single CSV row into a transaction"""
        
        # Get required fields
        date_str = row.get(self.config.date_column, "").strip()
        description = row.get(self.config.description_column, "").strip()
        amount_str = row.get(self.config.amount_column, "").strip()
        
        # Validate required fields
        if not date_str:
            raise ValueError(f"Missing date in column '{self.config.date_column}'")
        if not description:
            raise ValueError(f"Missing description in column '{self.config.description_column}'")
        if not amount_str:
            raise ValueError(f"Missing amount in column '{self.config.amount_column}'")
        
        # Parse date
        date = self._parse_date(date_str)
        
        # Parse amount
        amount = self._parse_amount(amount_str)
        
        # Get optional fields
        currency = "CHF"
        if self.config.currency_column:
            currency = row.get(self.config.currency_column, "CHF").strip() or "CHF"
        
        reference = None
        if self.config.reference_column:
            reference = row.get(self.config.reference_column, "").strip() or None
        
        # Generate reference if not provided
        if not reference:
            reference = self._generate_reference(date, description, amount)
        
        return ParsedTransaction(
            date=date,
            description=description,
            amount=amount,
            currency=currency,
            reference=reference,
            raw_data=dict(row),
        )
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date string and return ISO format (YYYY-MM-DD)"""
        try:
            dt = datetime.strptime(date_str, self.config.date_format)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            # Try common formats
            for fmt in ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"]:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            raise ValueError(f"Cannot parse date: {date_str}")
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        # Remove currency symbols and whitespace
        cleaned = amount_str.strip()
        for char in ["CHF", "EUR", "USD", "$", " ", "'"]:
            cleaned = cleaned.replace(char, "")
        
        # Handle Swiss/European format (1'234.56 or 1.234,56)
        if self.config.thousand_separator:
            cleaned = cleaned.replace(self.config.thousand_separator, "")
        
        # Handle decimal separator
        if self.config.decimal_separator != ".":
            cleaned = cleaned.replace(self.config.decimal_separator, ".")
        
        try:
            amount = float(cleaned)
            if self.config.negate_expenses and amount > 0:
                # Some banks use positive for expenses
                amount = -amount
            return amount
        except ValueError:
            raise ValueError(f"Cannot parse amount: {amount_str}")
    
    def _generate_reference(self, date: str, description: str, amount: float) -> str:
        """Generate a unique reference for duplicate detection"""
        data = f"{date}|{description}|{amount:.2f}"
        return f"CSV-{hashlib.md5(data.encode()).hexdigest()[:12].upper()}"


def create_sample_csv(filepath: str | Path, num_transactions: int = 20) -> None:
    """
    Create a sample CSV file in SpendWise format for testing.
    
    Args:
        filepath: Path to save the CSV file
        num_transactions: Number of transactions to generate
    """
    import random
    from datetime import date, timedelta
    
    samples = [
        ("MIGROS ZURICH HB", -45.80),
        ("SBB MOBILE", -25.00),
        ("ZALANDO ORDER", -89.90),
        ("NETFLIX.COM", -12.90),
        ("COOP PRONTO", -12.50),
        ("UBER RIDE", -18.40),
        ("SPOTIFY PREMIUM", -9.90),
        ("STARBUCKS ZURICH", -7.50),
        ("DENNER", -28.60),
        ("AMAZON.DE", -45.00),
        ("SALARY DEC", 4500.00),
        ("RENT PAYMENT", -1200.00),
        ("SWISSCOM BILL", -65.00),
        ("GYM MEMBERSHIP", -79.00),
    ]
    
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    today = date.today()
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "description", "amount", "currency", "reference"])
        
        for i in range(num_transactions):
            desc, amount = random.choice(samples)
            days_ago = random.randint(0, 30)
            tx_date = today - timedelta(days=days_ago)
            ref = f"TXN{i:06d}"
            
            writer.writerow([
                tx_date.isoformat(),
                desc,
                f"{amount:.2f}",
                "CHF",
                ref,
            ])
    
    print(f"Created sample CSV with {num_transactions} transactions: {filepath}")

