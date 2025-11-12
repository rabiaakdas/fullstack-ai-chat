FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Debug: Hangi dosyalar var?
RUN pwd
RUN ls -la

# Debug: .csproj dosyasını kontrol et
COPY . .
RUN ls -la
RUN find . -name "*.csproj"

# Sonra build işlemi
RUN dotnet restore
RUN dotnet publish -c Release -o /app

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build /app .
EXPOSE 80
ENV ASPNETCORE_URLS=http://+:80
ENTRYPOINT ["dotnet", "ChatAPI.dll"]
