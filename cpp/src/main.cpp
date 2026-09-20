#include "demo_io.hpp"
#include <array>
#include <iostream>

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--version") {
            std::cout << "RayCon-SLAM public preview " << DEMO_VERSION << '\n';
            return 0;
        }
        if (argc == 2 && std::string(argv[1]) == "--help") {
            std::cout << "Given planar odometry replay; no visual estimation.\n"
                         "Usage: raycon_slam_preview --input odometry.csv --output NEW_DIRECTORY\n";
            return 0;
        }
        auto args = demo::options(argc, argv, false);
        auto rows = demo::read_csv(args.at("--input"), {"timestamp", "dx_body_m", "dy_body_m", "dyaw_rad"});
        std::vector<std::array<double, 8>> poses;
        double x = 0, y = 0, yaw = 0, distance = 0, previous = 0;
        const double pi = std::acos(-1.0);
        for (const auto& row : rows) {
            double t = demo::number(row[0]), dx = demo::number(row[1]);
            double dy = demo::number(row[2]), dyaw = demo::number(row[3]);
            if (poses.empty() && (dx != 0 || dy != 0 || dyaw != 0))
                throw std::runtime_error("first row must have zero increments");
            if (!poses.empty() && t <= previous)
                throw std::runtime_error("timestamps must strictly increase");
            double c = std::cos(yaw), s = std::sin(yaw);
            x += c * dx - s * dy;
            y += s * dx + c * dy;
            yaw = std::remainder(yaw + dyaw, 2 * pi);
            distance += std::hypot(dx, dy);
            if (!std::isfinite(x) || !std::isfinite(y) || !std::isfinite(yaw) || !std::isfinite(distance))
                throw std::runtime_error("numeric overflow during replay");
            poses.push_back({t, x, y, 0, 0, 0, std::sin(yaw / 2), std::cos(yaw / 2)});
            previous = t;
        }
        double duration = poses.back()[0] - poses.front()[0];
        double end_distance = std::hypot(x, y);
        if (!std::isfinite(duration) || !std::isfinite(end_distance))
            throw std::runtime_error("numeric overflow in summary");
        std::ostringstream csv, tum, summary;
        csv << std::setprecision(17) << "timestamp,tx,ty,tz,qx,qy,qz,qw\n";
        tum << std::setprecision(17) << "# Public planar replay: timestamp tx ty tz qx qy qz qw\n";
        for (const auto& pose : poses) {
            for (std::size_t i = 0; i < pose.size(); ++i) {
                if (i) { csv << ','; tum << ' '; }
                csv << pose[i]; tum << pose[i];
            }
            csv << '\n'; tum << '\n';
        }
        summary << std::setprecision(17)
                << "{\n  \"version\": \"" << DEMO_VERSION << "\",\n"
                << "  \"mode\": \"public-demo\",\n  \"backend\": \"cpp_planar_odometry_replay\",\n"
                << "  \"pose_count\": " << poses.size() << ",\n"
                << "  \"path_length_m\": " << distance << ",\n"
                << "  \"duration_s\": " << duration << ",\n"
                << "  \"end_distance_from_origin_m\": " << end_distance << ",\n"
                << "  \"visual_tracking\": false,\n  \"loop_closure\": false\n}\n";
        const std::filesystem::path output = args.at("--output");
        demo::create_output(output);
        demo::write(output / "trajectory.csv", csv.str());
        demo::write(output / "trajectory.tum", tum.str());
        demo::write(output / "summary.json", summary.str());
        std::cout << "RayCon-SLAM v" << DEMO_VERSION << " | public preview\n"
                  << "Replayed " << poses.size() << " supplied poses. Output: " << output << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Input/output error: " << error.what() << '\n';
        return 2;
    }
}
