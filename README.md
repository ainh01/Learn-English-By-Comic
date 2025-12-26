# Quản lý điểm học sinh trung học phổ thông  

## 📋 Giới thiệu  
Hệ thống quản lý điểm học sinh trung học phổ thông được phát triển bằng C# và PostgreSQL.  

## 🛠️ Yêu cầu hệ thống  

- **Visual Studio 2022** (Community, Professional, hoặc Enterprise)  
- **PostgreSQL** (phiên bản 12 trở lên khuyến nghị)  
- **.NET Framework/Core** (tùy theo cấu hình project)  

## 📂 Cấu trúc thư mục  

```  
root/  
├── 📁 sql/  
│   ├── 📄 schema.sql      # Script tạo cấu trúc database  
│   └── 📄 seed.sql        # Script tạo dữ liệu mẫu  
└── 📁 StudentScoreManager/  
    └── Utils/  
        └── DatabaseConnection.cs  
```  

## 🚀 Hướng dẫn cài đặt  

### Bước 1: Cài đặt PostgreSQL  

1. Tải và cài đặt PostgreSQL từ [trang chủ](https://www.postgresql.org/download/)  
2. Ghi nhớ thông tin:  
   - Port (mặc định: 5432)  
   - Username (mặc định: postgres)  
   - Password (do bạn đặt khi cài đặt)  

### Bước 2: Tạo Database  

Mở **pgAdmin** hoặc **psql** và tạo database mới:  

```sql  
CREATE DATABASE qldiem;  
```  

### Bước 3: Chạy SQL Scripts  

Thực hiện **theo thứ tự**:  

#### 3.1. Chạy schema.sql (Tạo bảng)  

**Cách 1: Sử dụng psql**  
```bash  
psql -U postgres -d qldiem -f sql/schema.sql  
```  

**Cách 2: Sử dụng pgAdmin**  
- Kết nối tới database `qldiem`  
- Mở Query Tool (Tools → Query Tool)  
- Load file `sql/schema.sql` (File → Open)  
- Nhấn Execute/Run (F5 hoặc ▶️)  

#### 3.2. Chạy seed.sql (Thêm dữ liệu mẫu)  

**Cách 1: Sử dụng psql**  
```bash  
psql -U postgres -d qldiem -f sql/seed.sql  
```  

**Cách 2: Sử dụng pgAdmin**  
- Mở Query Tool  
- Load file `sql/seed.sql`  
- Nhấn Execute/Run (F5 hoặc ▶️)  

### Bước 4: Cấu hình Connection String  

#### Option 1: Sử dụng giá trị mặc định (Nhanh - Development)  

Ứng dụng đã được cấu hình với connection string mặc định:  

```csharp  
// Trong DatabaseConnection.cs  
if (string.IsNullOrEmpty(_connectionString))  
{  
    _connectionString = "Host=localhost;Port=5432;Database=qldiem;Username=postgres;Password=1704";  
    System.Diagnostics.Debug.WriteLine("WARNING: Using hardcoded connection string. Configure App.config for production.");  
}  
```  

**Nếu PostgreSQL của bạn dùng:**  
- Host: `localhost`  
- Port: `5432`  
- Database: `qldiem`  
- Username: `postgres`  
- Password: `1704`  

➡️ **Bạn có thể bỏ qua bước này và chạy trực tiếp!**  

#### Option 2: Thay đổi thông tin kết nối  

Nếu PostgreSQL của bạn có thông tin khác, mở file `StudentScoreManager/Utils/DatabaseConnection.cs` và chỉnh sửa:  

```csharp  
if (string.IsNullOrEmpty(_connectionString))  
{  
    _connectionString = "Host=localhost;Port=5432;Database=qldiem;Username=postgres;Password=YOUR_PASSWORD";  
    System.Diagnostics.Debug.WriteLine("WARNING: Using hardcoded connection string. Configure App.config for production.");  
}  
```  

**Thay đổi các thông số cho phù hợp:**  
- `Host`: localhost (hoặc IP server)  
- `Port`: 5432 (hoặc port bạn đã cấu hình)  
- `Database`: qldiem  
- `Username`: postgres (hoặc user của bạn)  
- `Password`: **MẬT KHẨU CỦA BẠN**  

#### Option 3: Sử dụng App.config (Khuyến nghị cho Production)  

Thêm vào file `App.config`:  

```xml  
<?xml version="1.0" encoding="utf-8" ?>  
<configuration>  
  <connectionStrings>  
    <add name="PostgreSQL"   
         connectionString="Host=localhost;Port=5432;Database=qldiem;Username=postgres;Password=YOUR_PASSWORD"   
         providerName="Npgsql" />  
  </connectionStrings>  
</configuration>  
```  

### Bước 5: Mở Project trong Visual Studio 2022  

1. Mở **Visual Studio 2022**  
2. Click **File** → **Open** → **Project/Solution**  
3. Chọn file solution (`.sln`) trong thư mục `StudentScoreManager`  
4. Đợi Visual Studio restore các NuGet packages (tự động)  

### Bước 6: Chạy ứng dụng  

1. Nhấn **F5** để chạy với debugging  
2. Hoặc nhấn **Ctrl + F5** để chạy without debugging  
3. Kiểm tra Output window để xem thông báo kết nối  

## ✅ Kiểm tra cài đặt  

Sau khi chạy, kiểm tra:  
- [ ] Ứng dụng khởi động không lỗi  
- [ ] Kết nối database thành công  
- [ ] Hiển thị dữ liệu mẫu từ seed.sql  
- [ ] Xem Output/Debug window để kiểm tra warning messages  

## ❗ Xử lý lỗi thường gặp  

### Lỗi: "Could not connect to server" / "Connection refused"  
**Nguyên nhân:** PostgreSQL service không chạy hoặc cấu hình sai  

**Giải pháp:**  
- ✅ Kiểm tra PostgreSQL service đang chạy:  
  - Windows: Services → PostgreSQL → Status: Running  
  - Hoặc Task Manager → Services → postgresql-x64-xx  
- ✅ Kiểm tra port 5432 có đang sử dụng: `netstat -an | findstr 5432`  
- ✅ Kiểm tra firewall cho phép port 5432  

### Lỗi: "Password authentication failed for user"  
**Nguyên nhân:** Sai username hoặc password  

**Giải pháp:**  
- ✅ Đảm bảo password PostgreSQL của bạn là `1704` hoặc thay đổi trong code  
- ✅ Kiểm tra user `postgres` tồn tại và có quyền truy cập  
- ✅ Reset password PostgreSQL nếu cần:  
  ```sql  
  ALTER USER postgres PASSWORD '1704';  
  ```  

### Lỗi: "Database 'qldiem' does not exist"  
**Nguyên nhân:** Chưa tạo database  

**Giải pháp:**  
- ✅ Chạy lại Bước 2:  
  ```sql  
  CREATE DATABASE qldiem;  
  ```  
- ✅ Kiểm tra database đã tồn tại:  
  ```sql  
  \l  -- trong psql  
  ```  

### Lỗi: "Relation does not exist" / "Table not found"  
**Nguyên nhân:** Chưa chạy schema.sql  

**Giải pháp:**  
- ✅ Chạy lại `schema.sql` theo Bước 3.1  
- ✅ Kiểm tra kết nối đúng database `qldiem`  

### Lỗi: "Npgsql.dll not found" / "Could not load Npgsql"  
**Nguyên nhân:** Thiếu NuGet package  

**Giải pháp:**  
- ✅ Restore NuGet packages:  
  - Chuột phải vào Solution → **Restore NuGet Packages**  
  - Hoặc: Tools → NuGet Package Manager → Package Manager Console  
  - Chạy: `Update-Package -reinstall`  

### Warning: "Using hardcoded connection string"  
**Đây không phải lỗi!** Đây là cảnh báo khi dùng hardcoded connection string.  

**Để tắt warning này trong production:**  
- ✅ Cấu hình App.config (xem Option 3 ở Bước 4)  

## 📝 Ghi chú quan trọng  

### Bảo mật  
- ⚠️ **KHÔNG commit** file chứa password lên Git/GitHub  
- 🔒 Trong production, sử dụng:  
  - App.config với connection string  
  - Environment variables  
  - Secure configuration management  
- 💡 Thêm `DatabaseConnection.cs` vào `.gitignore` nếu chứa thông tin nhạy cảm  

### Development vs Production  
- 🛠️ **Development:** Dùng hardcoded connection string (hiện tại)  
- 🚀 **Production:** Dùng App.config hoặc environment variables  
- 📌 Password mặc định `1704` chỉ dùng cho môi trường phát triển  

### Best Practices  
- ✨ Tạo user PostgreSQL riêng cho ứng dụng (không dùng `postgres` superuser)  
- ✨ Sử dụng connection pooling  
- ✨ Xử lý exception khi kết nối database  

## 🔧 Cấu hình nâng cao  

### Tạo user riêng cho ứng dụng  

```sql  
-- Tạo user mới  
CREATE USER qldiem_user WITH PASSWORD 'your_secure_password';  

-- Cấp quyền  
GRANT ALL PRIVILEGES ON DATABASE qldiem TO qldiem_user;  
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO qldiem_user;  
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO qldiem_user;  

-- Update connection string  
"Host=localhost;Port=5432;Database=qldiem;Username=qldiem_user;Password=your_secure_password"  
```  

## 📞 Hỗ trợ  

Nếu gặp vấn đề:  
1. ✅ Kiểm tra lại từng bước cài đặt  
2. ✅ Xem phần "Xử lý lỗi thường gặp"  
3. ✅ Kiểm tra Output/Debug window trong Visual Studio  
4. ✅ Kiểm tra PostgreSQL logs  
5. ✅ Liên hệ team phát triển  

---  

## 🌐 English Version (Quick Setup)  

### Quick Installation Steps  

1. **Install PostgreSQL** and create database:  
   ```sql  
   CREATE DATABASE qldiem;  
   ```  

2. **Run SQL scripts** in order:  
   ```bash  
   psql -U postgres -d qldiem -f sql/schema.sql  
   psql -U postgres -d qldiem -f sql/seed.sql  
   ```  

3. **Configure connection** (if different from default):  
   - Default: `Host=localhost;Port=5432;Database=qldiem;Username=postgres;Password=1704`  
   - Edit `StudentScoreManager/Utils/DatabaseConnection.cs` if needed  

4. **Open in Visual Studio 2022** and run (F5)  

### Default Connection String  
```csharp  
"Host=localhost;Port=5432;Database=qldiem;Username=postgres;Password=1704"  
```  

### Troubleshooting  
- **Connection failed:** Check PostgreSQL service is running  
- **Auth failed:** Verify password is `1704` or update in code  
- **Database not found:** Run `CREATE DATABASE qldiem;`  
- **Npgsql error:** Restore NuGet packages  

---  

**Version:** 1.2.999  
**Last Updated:** 2025  
**Database:** PostgreSQL  
**Framework:** .NET (Visual Studio 2022)
