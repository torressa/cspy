file(GLOB DOTNET_SRCS "*.cs")
foreach(FILE_NAME IN LISTS DOTNET_SRCS)
  add_dotnet_test(${FILE_NAME})
endforeach()
