import model
import reading_data

if __name__ == '__main__':
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # Leave this code uncommented when you submit your files.

    # Get DataFrame
    df = model.process_dataframe(model.make_dataframe(reading_data.loading_data()))

    # Plot graphs
    model.plot_graphs(df)

    # Split into Independent and Dependent Arrays
    data = model.separate_indepedent_dependent(df)

    # Split training and testing set
    split_data = model.split_data(data)

    # Transform training set
    transformations = model.get_data_transformations(model.split_data(data))
    transformed_data = model.transform_data(split_data, transformations)

    # Get best model
    best_predictor = model.tune_model(transformed_data, model.
                                      select_best_model(data, transformed_data, transformations))

    # Make predictions
    predictions = model.make_predictions(df, transformations, best_predictor)

    # Visualize predictions
    model.visualize_predictions(df, predictions)

    # import python_ta
    #
    # python_ta.check_all(config={
    #     'extra-imports': ['model', 'reading_data']
    # })
