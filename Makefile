# Run unit tests
all:
	cmake -S . -Bbuild -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
	cmake --build build --config Release --target all -v
	cd build && ctest --verbose

# Run benchmarks
benchmark:
	cmake -S . -Bbuild -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
				-DBENCHMARK_TESTS=ON
	cmake --build build --config Release --target all -v
	cd build && ctest --verbose

# Build and test python interface
p:
	cmake -S . -Bbuild -DCMAKE_BUILD_TYPE=Release  -DBUILD_TESTING=ON \
      -DBUILD_PYTHON=ON -DBUILD_SHARED_LIBS=ON
	cmake --build build --config Release --target all -v
	cd build && ctest --verbose -R python_unittest

d:
	cmake -S . -Bbuild -DCMAKE_BUILD_TYPE=Release  -DBUILD_TESTING=ON \
      -DBUILD_DOTNET=ON -DBUILD_SHARED_LIBS=ON
	cmake --build build --config Release --target all -v
	cd build && ctest --verbose 

# Run benchmarks using boost (as well as cspy)
benchmarks_boost:
	cmake -S . -Bbuild -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
    -DBENCHMARK_TESTS=ON -DBENCHMARK_BOOST=ON -DBUILD_SHARED_LIBS=OFF
	cmake --build build --config Release --target all -v
	cd build && ctest --verbose

clean:
	rm -rf build
