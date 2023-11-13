# import numpy as np
# import rasterio
# from numpy.lib.stride_tricks import sliding_window_view
# from preprocess import robust_normalize


# def main():
#     np.random.seed(0)
#     band = np.random.rand(0(10, 10), dtype="uint16")
#     normalized_band = robust_normalize(band)
#     # print(normalized_band)
#     print(normalized_band.dtype)


# def test_moving_window():
#     KERNEL_SIZE = 256
#     STEP_SIZE = 236  # Define the step size
#     metadata = {"height": 10980, "width": 10980}
#     stacked_bands = np.ones((10980, 10980, 4), dtype="uint16")
#     stacked_bands = pad_image(stacked_bands, KERNEL_SIZE, STEP_SIZE)  # Pad the image
#     num_rows = (metadata["height"] - KERNEL_SIZE) // STEP_SIZE + 1
#     num_cols = (metadata["width"] - KERNEL_SIZE) // STEP_SIZE + 1
#     for row in range(num_rows + 1):
#         for col in range(num_cols + 1):
#             print(row, col)
#             # Define the window coordinates for the snippet
#             window = rasterio.windows.Window(
#                 col * STEP_SIZE, row * STEP_SIZE, KERNEL_SIZE, KERNEL_SIZE
#             )

#             # Cut out the snippet from the merged image
#             small_image = stacked_bands[
#                 window.row_off : window.row_off + window.height,
#                 window.col_off : window.col_off + window.width,
#             ]
#             assert small_image.shape == (256, 256, 4)


# def pad_image(image, kernel_size, step_size):
#     """
#     Pads an image so that windows of the given kernel size and step size cover the entire image.

#     Args:
#     image (np.array): The image to pad.
#     kernel_size (int): The size of the kernel.
#     step_size (int): The size of the step.

#     Returns:
#     np.array: The padded image.
#     """
#     height, width, _ = image.shape
#     pad_height = (kernel_size - height % step_size) % step_size
#     pad_width = (kernel_size - width % step_size) % step_size
#     return np.pad(
#         image,
#         ((0, pad_height), (0, pad_width), (0, 0)),
#         mode="constant",
#         constant_values=0,
#     )


# def count_zeros(array):
#     """
#     Counts the number of zeros in a numpy array.

#     Args:
#     array (np.array): The array to count zeros in.

#     Returns:
#     int: The number of zeros in the array.
#     """
#     return np.size(array) - np.count_nonzero(array)


# if __name__ == "__main__":
#     main()
