const path = require("path");

module.exports = {
  mode: "production",
  entry: {    
    index: "./src/index.ts",
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: {
          loader: "ts-loader",
          options: {
            compilerOptions: {
              sourceMap: true,
            },
          },
        },
      },
    ],
  },
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
  },
  output: {
    filename: "monofy-photo.js",
    path: path.resolve(__dirname, "dist", "js"),
    library: "monofy",
    sourceMapFilename: "monofy-photo.js.map",    
  },
  devtool: "source-map",  
};
