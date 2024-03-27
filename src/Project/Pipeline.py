def run_pipeline():
    # Load data
    data = load_data()
    # Preprocess data
    data = preprocess_data(data)
    # Train model
    model = train_model(data)
    # Evaluate model
    evaluate_model(model, data)
    # Save model
    save_model(model)