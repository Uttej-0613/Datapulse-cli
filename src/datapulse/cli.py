import argparse
import sys
from pathlib import Path
from .loaders import load_and_clean_csv
from .trainer import train_model, predict_age

def main():
    parser = argparse.ArgumentParser(description="DataPulse - CSV Validator & Trainer")
    parser.add_argument("filepath", help="Path to the CSV file")
    parser.add_argument("--train", action="store_true", help="Train ML model after validation")
    parser.add_argument("--predict", type=int, help="Predict salary for a given age (requires --train or existing model)")
    args = parser.parse_args()
    
    try:
        # Step 1: Load and clean
        clean_data = load_and_clean_csv(args.filepath)
        
        if args.train:
            print("\n🚀 Training ML model...")
            result = train_model(clean_data)
            print(f"📈 R² Score: {result['r2_score']:.4f}")
            print(f"📐 Formula: Salary = {result['slope']:.2f} * Age + {result['intercept']:.2f}")
            print(f"💾 Model saved to: {result['model_path']}")
            
            if args.predict:
                pred = predict_age(result['model'], args.predict)
                print(f"🔮 Prediction for Age {args.predict}: ${pred:,.2f}")
        
        elif args.predict:
            # Load existing model
            import pickle
            with open("salary_predictor.pkl", 'rb') as f:
                model = pickle.load(f)
            pred = predict_age(model, args.predict)
            print(f"🔮 Prediction for Age {args.predict}: ${pred:,.2f}")
        
        else:
            print("\n✅ Validation complete. Use --train to train a model.")
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
