# Phenikaa GPA Planner

**Website hỗ trợ lập kế hoạch học tập và tính GPA cho sinh viên
Phenikaa**

Phenikaa GPA Planner là hệ thống hỗ trợ sinh viên Đại học Phenikaa theo
dõi tiến độ học tập, tính toán GPA, xây dựng lộ trình học tập và đánh
giá các điều kiện tốt nghiệp. Hệ thống thu thập dữ liệu từ cổng Quản lý
đào tạo (QLĐT), đối chiếu chương trình đào tạo với bảng điểm thực tế,
sau đó cung cấp các công cụ phân tích, gợi ý và mô phỏng kế hoạch học
tập.

-   **Tên đề tài:** Xây dựng website hỗ trợ lập kế hoạch học tập và tính
    GPA cho sinh viên Phenikaa
-   **Tên hệ thống:** Phenikaa GPA Planner
-   **Repository:**
    [ngananh5920-cmyk/Phenikaa-Advister](https://github.com/ngananh5920-cmyk/Phenikaa-Advister)
-   **Đơn vị:** Trường Công nghệ Thông tin Phenikaa -- Đại học Phenikaa

------------------------------------------------------------------------

## 1. Bài toán và mục tiêu

Trong chương trình đào tạo theo tín chỉ, sinh viên phải chủ động theo
dõi kết quả học tập, điều kiện tiên quyết và các yêu cầu của chương
trình đào tạo. Tuy nhiên, dữ liệu về chương trình học, bảng điểm và kết
quả đăng ký thường nằm ở nhiều trang khác nhau trên cổng QLĐT.

Phenikaa GPA Planner được xây dựng để giải quyết những khó khăn đó:

-   Tổng hợp dữ liệu học tập từ nhiều trang QLĐT thành một nguồn thông
    tin thống nhất.
-   Xác định học phần đã hoàn thành, đang học, có thể đăng ký, bị khóa
    hoặc cần học lại.
-   Theo dõi tín chỉ đã tích lũy và tín chỉ còn thiếu theo từng khối
    kiến thức.
-   Tính GPA cần đạt để hướng tới mục tiêu xếp loại mong muốn.
-   Đề xuất học phần học cải thiện và học phần nên đăng ký trong các học
    kỳ tiếp theo.
-   Mô phỏng kế hoạch học tập nhiều học kỳ và kiểm tra điều kiện tốt
    nghiệp.
-   Theo dõi lịch học và xuất lịch sang các ứng dụng lịch.

Hệ thống chỉ đọc dữ liệu từ QLĐT, không ghi hoặc thay đổi dữ liệu trên
cổng đào tạo.

## 2. Chức năng chính

### 2.1. Cập nhật dữ liệu từ QLĐT

Hệ thống sử dụng Playwright để điều khiển Chrome/Chromium, đăng nhập và
thu thập dữ liệu từ cổng QLĐT.

Dữ liệu được thu thập gồm:

-   Chương trình đào tạo.
-   Bảng điểm và kết quả học tập.
-   Kết quả đăng ký học phần.
-   Lịch học chi tiết của từng lớp học phần.

Hệ thống hỗ trợ bốn chế độ truy cập:

  -----------------------------------------------------------------------
  Chế độ                              Mô tả
  ----------------------------------- -----------------------------------
  `cdp`                               Sử dụng cửa sổ Chrome riêng với
                                      profile lưu lâu dài và Chrome
                                      DevTools Protocol

  `profile`                           Tận dụng phiên đăng nhập sẵn có của
                                      Chrome

  `manual`                            Sinh viên tự đăng nhập trong cửa sổ
                                      trình duyệt

  `remote`                            Đăng nhập trên trình duyệt từ xa
                                      được hiển thị trong giao diện web
                                      thông qua noVNC
  -----------------------------------------------------------------------

Quá trình thu thập dữ liệu có nhật ký cập nhật theo thời gian thực thông
qua Server-Sent Events (SSE).

### 2.2. Tổng quan tiến độ học tập

-   Tổng hợp số tín chỉ đã tích lũy và số tín chỉ còn thiếu.
-   Theo dõi tiến độ theo từng khối kiến thức.
-   Hiển thị các học phần đang học và học phần chưa đạt.
-   Theo dõi GPA và các thông tin học vụ liên quan.

### 2.3. Danh sách và tra cứu học phần

Học phần được phân loại theo trạng thái:

  Trạng thái         Ý nghĩa
  ------------------ ----------------------------------------------
  `HOAN_THANH`       Học phần đã học và đạt
  `DANG_KY_KY_NAY`   Học phần đang đăng ký trong học kỳ hiện tại
  `CO_THE_DANG_KY`   Đã đáp ứng điều kiện tiên quyết
  `BI_KHOA`          Chưa đáp ứng ít nhất một học phần tiên quyết
  `CAN_HOC_LAI`      Học phần chưa đạt
  `KHONG_BAT_BUOC`   Học phần tự chọn thuộc khối đã đủ tín chỉ

Sinh viên có thể tìm kiếm học phần và xem các môn tiên quyết còn thiếu
đối với học phần đang bị khóa.

### 2.4. Hỗ trợ học tập và mục tiêu GPA

Sinh viên có thể lựa chọn mục tiêu GPA theo các mốc:

-   Khá: 2.50.
-   Giỏi: 3.20.
-   Xuất sắc: 3.60.
-   Hoặc nhập mục tiêu tùy chỉnh trong khoảng 2.00--4.00.

Hệ thống tính GPA cần đạt ở phần tín chỉ còn lại và đánh giá tính khả
thi của mục tiêu. Khi mục tiêu chưa khả thi, hệ thống có thể đưa ra mức
GPA tối đa dự kiến theo phương án cải thiện.

### 2.5. Gợi ý học cải thiện

-   Xác định các học phần đã đạt có điểm từ B trở xuống (≤ 3.0) là ứng
    viên cải thiện.
-   Ước tính tác động của điểm mới đến GPA.
-   Điểm mới thay thế điểm cũ của chính học phần đó; không cộng thêm tín
    chỉ vào mẫu số GPA.
-   Ưu tiên phương án sử dụng số học phần cải thiện ít nhất theo thuật
    toán của hệ thống.

### 2.6. Gợi ý học phần và lộ trình học tập

Hệ thống xây dựng gợi ý học phần cho các học kỳ tiếp theo theo ba mức
cường độ:

-   8--10 tín chỉ.
-   11--13 tín chỉ.
-   14--16 tín chỉ.

Thuật toán xem xét học phần bắt buộc, học lại, học phần tự chọn còn
thiếu, điều kiện tiên quyết và mức ưu tiên của từng học phần. Từ kế
hoạch được xếp theo từng kỳ, hệ thống ước lượng thời điểm hoàn thành
chương trình.

### 2.7. Mô phỏng và lưu kế hoạch học tập

-   Tạo kế hoạch học tập gồm nhiều học kỳ.
-   Thêm học phần vào từng học kỳ.
-   Kiểm tra điều kiện tiên quyết và học phần trùng lặp.
-   Kiểm tra giới hạn tín chỉ từ 8 đến 16 tín chỉ mỗi kỳ (trừ trường hợp
    số tín chỉ còn lại ít hơn 8).
-   Lưu, chỉnh sửa và xóa kế hoạch.

### 2.8. Kiểm tra điều kiện tốt nghiệp

Hệ thống tổng hợp các điều kiện xét tốt nghiệp thành danh sách trạng
thái, bao gồm:

-   Tín chỉ theo các khối kiến thức.
-   Học phần bắt buộc còn phải học lại.
-   GPA tối thiểu.
-   Giáo dục thể chất.
-   Các điều kiện cần sinh viên tự xác nhận khi QLĐT không cung cấp dữ
    liệu, như ngoại ngữ, tin học, kỷ luật, nghĩa vụ tài chính và Giáo
    dục quốc phòng -- an ninh.

Kết quả được thể hiện theo các trạng thái như đủ điều kiện, chờ xác nhận
hoặc chưa đủ điều kiện.

### 2.9. Cảnh báo học vụ

-   Tính GPA từng học kỳ và GPA tích lũy theo điểm cao nhất.
-   Theo dõi cảnh báo học tập theo Điều 21.
-   Kiểm tra tỷ lệ học lại vượt 5% tổng tín chỉ theo Điều 27.7 của quy
    chế được sử dụng trong hệ thống.

### 2.10. Lịch học và tích hợp ứng dụng lịch

-   Hiển thị lịch học theo tuần.
-   Xuất lịch dưới dạng tệp `.ics`.
-   Cung cấp URL đăng ký lịch để ứng dụng lịch có thể tự cập nhật.
-   Hỗ trợ các ứng dụng tương thích iCalendar như Google Calendar, Apple
    Calendar và Outlook.

## 3. Quy trình hoạt động

``` mermaid
flowchart TD
    A["Sinh viên mở Phenikaa GPA Planner"] --> B["Cập nhật dữ liệu từ QLĐT"]
    B --> C["Đăng nhập Microsoft SSO"]
    C --> D["Crawler thu thập chương trình, bảng điểm, kết quả đăng ký và lịch học"]
    D --> E["Phân tích HTML và chuẩn hóa dữ liệu"]
    E --> F["Đối chiếu chương trình đào tạo với bảng điểm"]
    F --> G["Tạo roadmap và tính toán dữ liệu học tập"]
    G --> H["Tổng quan và tra cứu học phần"]
    G --> I["Hỗ trợ học tập và mục tiêu GPA"]
    G --> J["Kiểm tra điều kiện tốt nghiệp"]
    G --> K["Mô phỏng và lưu kế hoạch"]
    G --> L["Xem và xuất lịch học"]
```

Sau khi dữ liệu được cập nhật, các chức năng tính toán, gợi ý và mô
phỏng sử dụng dữ liệu đã lưu, không cần truy cập lại QLĐT cho mỗi thao
tác.

## 4. Kiến trúc hệ thống

Hệ thống được tổ chức thành các thành phần chính:

  ---------------------------------------------------------------------------
  Thành phần              Công nghệ / tệp chính       Trách nhiệm
  ----------------------- --------------------------- -----------------------
  Front-end               HTML, CSS, JavaScript       Giao diện, gọi REST
                          (`frontend/index.html`,     API, nhận nhật ký crawl
                          `app.js`, `style.css`)      qua SSE

  Back-end                Python, Flask (`server.py`) Cung cấp API, quản lý
                                                      phiên, điều phối tiến
                                                      trình crawl

  Crawler                 Playwright                  Điều khiển trình duyệt,
                          (`crawler_with_login.py`)   đăng nhập QLĐT và thu
                                                      thập dữ liệu

  Xử lý dữ liệu           BeautifulSoup4, lxml,       Phân tích HTML, chuẩn
                          html5lib, pandas            hóa và đối chiếu dữ
                          (`build_roadmap.py`)        liệu

  Học vụ                  `hoc_vu.py`                 Tính GPA theo học kỳ,
                                                      GPA tích lũy và cảnh
                                                      báo học vụ

  Lập kế hoạch            `planner.py`                Xếp học phần theo học
                                                      kỳ và cường độ học

  Hỗ trợ học tập          `advisor.py`                Tính GPA mục tiêu, gợi
                                                      ý học cải thiện và lộ
                                                      trình

  Mô phỏng                `academic_simulator.py`     Kiểm tra và lưu kế
                                                      hoạch nhiều học kỳ

  Tốt nghiệp              `graduation_check.py`       Kiểm tra các điều kiện
                                                      tốt nghiệp

  Lịch học                `class_schedule.py`         Thu thập lịch lớp học
                                                      phần và tạo dữ liệu
                                                      iCalendar

  Lưu trữ                 JSON và HTML                Lưu dữ liệu riêng theo
                                                      từng người dùng
  ---------------------------------------------------------------------------

### Mô hình triển khai

Hệ thống hỗ trợ hai cách vận hành:

**Chạy cục bộ**

-   Chạy Flask trên máy cá nhân.
-   Mở giao diện tại `http://localhost:5000`.
-   Có thể sử dụng Chrome/Chromium cục bộ để đăng nhập và thu thập dữ
    liệu.

**Triển khai trên VPS**

-   Docker Compose quản lý các dịch vụ.
-   Gunicorn chạy ứng dụng Flask.
-   Nginx làm reverse proxy cho HTTP, SSE và WebSocket.
-   Xvfb, Fluxbox, Chromium, x11vnc và noVNC hỗ trợ trình duyệt từ xa.
-   Mỗi phiên crawl có môi trường trình duyệt riêng; sau khi hoàn tất,
    tiến trình của job được dừng để giải phóng tài nguyên.

## 5. Công nghệ sử dụng

  Nhóm                           Công nghệ
  ------------------------------ -------------------------------------------------
  Ngôn ngữ phía máy chủ          Python 3.12
  Web framework                  Flask 3.x, Flask-Cors
  WebSocket                      flask-sock
  WSGI server                    Gunicorn
  Browser automation             Playwright for Python, Chrome DevTools Protocol
  Phân tích HTML                 BeautifulSoup4, lxml, html5lib
  Xử lý dữ liệu                  pandas
  Front-end                      HTML, CSS, JavaScript thuần
  Giao tiếp thời gian thực       Server-Sent Events (SSE), WebSocket
  Lưu trữ                        JSON, HTML theo từng người dùng
  Kiểm thử                       pytest
  Đóng gói và triển khai         Docker, Docker Compose, nginx
  Môi trường trình duyệt từ xa   Xvfb, Fluxbox, x11vnc, noVNC

## 6. Lưu trữ dữ liệu và bảo mật

Hệ thống không sử dụng hệ quản trị cơ sở dữ liệu quan hệ. Dữ liệu được
lưu bằng các tệp JSON/HTML trong thư mục riêng theo `client_id` của từng
trình duyệt:

``` text
data/
└── users/
    └── <client_id>/
        ├── roadmap.json
        ├── lich_hoc_phan.json
        ├── study_plans.json
        ├── graduation_self.json
        └── ...
```

Một số nguyên tắc bảo mật được áp dụng:

-   Không lưu mật khẩu QLĐT xuống đĩa và không ghi mật khẩu vào nhật ký.
-   Hỗ trợ sinh viên tự đăng nhập trực tiếp trong trình duyệt.
-   Phiên làm việc sử dụng cookie `HttpOnly`, `SameSite=Lax` và có thể
    bật `Secure`.
-   Dữ liệu học tập được tách riêng theo từng `client_id`.
-   Cổng VNC chỉ lắng nghe trên `127.0.0.1`; WebSocket kiểm tra phiên sở
    hữu job.
-   Token đăng ký lịch được tạo riêng cho từng người dùng.

## 7. Cài đặt và chạy

### Yêu cầu

-   Python 3.12.
-   Google Chrome hoặc Chromium.
-   Git.
-   Tài khoản QLĐT và kết nối Internet để cập nhật dữ liệu.

### Lấy mã nguồn

``` bash
git clone https://github.com/ngananh5920-cmyk/Phenikaa-Advister.git
cd Phenikaa-Advister
```

### Cài đặt thư viện

``` bash
pip install -r requirements.txt
```

### Chạy cục bộ

``` bash
python server.py
```

Sau khi máy chủ khởi động, mở:

``` text
http://localhost:5000
```

### Chạy bằng Docker Compose

Nếu sử dụng cấu hình Docker Compose có sẵn trong repository:

``` bash
docker compose up -d --build
```

Để dừng các dịch vụ:

``` bash
docker compose down
```

> Lưu ý: Các lệnh trên giả định repository có `requirements.txt`,
> `Dockerfile` và cấu hình Docker Compose tương ứng. Hãy kiểm tra cấu
> trúc phiên bản mã nguồn đang sử dụng trước khi chạy.

## 8. Kiểm thử

Theo báo cáo đồ án, nhóm đã thực hiện bộ kiểm thử tự động gồm **127 ca
kiểm thử**, với kết quả được ghi nhận:

  Chỉ số                     Kết quả
  ------------------------ ---------
  Tổng số ca kiểm thử            127
  Số ca đạt (PASS)               127
  Số ca không đạt (FAIL)           0
  Tỷ lệ đạt                     100%

Báo cáo cũng đề cập đến kiểm thử chức năng tự điền đăng nhập
(`test_login_autofill.py`) và kịch bản kiểm thử đầu cuối trên trang đăng
nhập giả bằng Chromium thật (`e2e_mock_login.py`).

Các module tính toán được thiết kế theo hướng hàm thuần để có thể kiểm
thử bằng pytest mà không cần khởi chạy trình duyệt.

## 9. Hạn chế hiện tại

Theo phạm vi được nêu trong báo cáo:

-   Crawler phụ thuộc vào cấu trúc trang QLĐT; thay đổi giao diện có thể
    yêu cầu cập nhật bộ thu thập dữ liệu.
-   Kết quả gợi ý, cảnh báo và kiểm tra tốt nghiệp chỉ mang tính tham
    khảo, không thay thế việc xét duyệt chính thức.
-   Một số cách diễn giải quy chế cần được đối chiếu thêm với Phòng Đào
    tạo.
-   Dữ liệu hiện gắn với phiên trình duyệt, chưa có tài khoản đồng bộ đa
    thiết bị.
-   Các job crawl được quản lý trong bộ nhớ của một tiến trình.
-   Giao diện hiện tối ưu cho máy tính, chưa tối ưu cho điện thoại.
-   Chưa kiểm chứng đầy đủ khả năng áp dụng cho nhiều ngành và chương
    trình đào tạo khác nhau.

## 10. Định hướng phát triển

-   Bổ sung tài khoản cá nhân và xác thực bảo mật hai lớp.
-   Đồng bộ dữ liệu học tập giữa máy tính, điện thoại và máy tính bảng.
-   Chuyển sang cơ sở dữ liệu chuyên dụng như PostgreSQL, MySQL hoặc
    MongoDB.
-   Hoàn thiện giao diện responsive cho thiết bị di động.
-   Bổ sung thông báo về lịch học, lịch thi, học phí và thời gian đăng
    ký tín chỉ.
-   Mở rộng kiểm thử tích hợp HTTP, kiểm thử end-to-end giao diện và
    kiểm thử crawler trên môi trường phù hợp.
-   Mở rộng dữ liệu chương trình đào tạo và xử lý linh hoạt các trường
    hợp đặc biệt theo quy chế đào tạo.

## 11. Nhóm thực hiện

  Thành viên           Mã sinh viên
  -------------------- --------------
  Đỗ Nguyên Anh Vũ     23010334
  Nguyễn Phương Ngân   23010450

**Giảng viên hướng dẫn:** ThS. Trịnh Thanh Bình

**Đơn vị:** Trường Công nghệ Thông tin Phenikaa -- Đại học Phenikaa

## 12. Tài liệu tham khảo

-   [Flask Documentation](https://flask.palletsprojects.com/)
-   [Playwright for Python](https://playwright.dev/python/)
-   [Chrome DevTools
    Protocol](https://chromedevtools.github.io/devtools-protocol/)
-   [Beautiful Soup
    Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
-   [pandas Documentation](https://pandas.pydata.org/docs/)
-   [Gunicorn Documentation](https://docs.gunicorn.org/)
-   [Docker Documentation](https://docs.docker.com/)
-   [noVNC](https://novnc.com/)
-   [RFC 5545 -- iCalendar](https://www.rfc-editor.org/rfc/rfc5545)
-   Trường Đại học Phenikaa, *Quy chế đào tạo trình độ đại học*, Quyết
    định số 1062/QĐ-ĐHP-ĐT ngày 20/07/2023.

------------------------------------------------------------------------

*Phenikaa GPA Planner -- Chủ động theo dõi tiến độ, lập kế hoạch học tập
và hướng tới mục tiêu tốt nghiệp.*
